from __future__ import annotations

import logging
from collections.abc import Sequence
from types import TracebackType
from typing import Any

import aiohttp
from aiohttp import ClientResponseError
from yarl import URL

from .entities import (
    BucketsConfig,
    Cluster,
    CredentialsConfig,
    DisksConfig,
    DNSConfig,
    IngressConfig,
    MetricsConfig,
    MonitoringConfig,
    OrchestratorConfig,
    RegistryConfig,
    SecretsConfig,
    StorageConfig,
)
from .factories import EntityFactory, PayloadFactory

logger = logging.getLogger(__name__)


class ConfigClient:
    def __init__(
        self,
        url: URL,
        token: str,
        timeout: aiohttp.ClientTimeout = aiohttp.client.DEFAULT_TIMEOUT,
        trace_configs: Sequence[aiohttp.TraceConfig] = (),
    ):
        self._clusters_url = url / "api/v1/clusters"
        self._token = token
        self._timeout = timeout
        self._trace_configs = trace_configs
        self._client: aiohttp.ClientSession | None = None
        self._entity_factory = EntityFactory()
        self._payload_factory = PayloadFactory()

    async def __aenter__(self) -> "ConfigClient":
        self._client = await self._create_http_client()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        assert self._client
        await self._client.close()

    async def _create_http_client(self) -> aiohttp.ClientSession:
        client = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self._token}"},
            timeout=self._timeout,
            trace_configs=list(self._trace_configs),
        )
        return await client.__aenter__()

    async def get_clusters(self) -> Sequence[Cluster]:
        assert self._client
        async with self._client.get(self._clusters_url) as response:
            response.raise_for_status()
            payload = await response.json()
            return [self._entity_factory.create_cluster(p) for p in payload]

    async def get_cluster(self, name: str) -> Cluster:
        assert self._client
        async with self._client.get(self._clusters_url / name) as response:
            response.raise_for_status()
            payload = await response.json()
            return self._entity_factory.create_cluster(payload)

    async def create_blank_cluster(
        self, name: str, token: str, ignore_existing: bool = False
    ) -> Cluster:
        assert self._client
        payload = {"name": name, "token": token}
        try:
            async with self._client.post(self._clusters_url, json=payload) as resp:
                resp.raise_for_status()
                resp_payload = await resp.json()
                return self._entity_factory.create_cluster(resp_payload)
        except ClientResponseError as e:
            is_existing = e.status == 400 and "already exists" in e.message
            if not ignore_existing or is_existing:
                raise
        return await self.get_cluster(name)

    async def update_cluster(
        self,
        name: str,
        *,
        credentials: CredentialsConfig | None = None,
        storage: StorageConfig | None = None,
        registry: RegistryConfig | None = None,
        orchestrator: OrchestratorConfig | None = None,
        monitoring: MonitoringConfig | None = None,
        secrets: SecretsConfig | None = None,
        metrics: MetricsConfig | None = None,
        disks: DisksConfig | None = None,
        buckets: BucketsConfig | None = None,
        ingress: IngressConfig | None = None,
        dns: DNSConfig | None = None,
    ) -> Cluster:
        assert self._client
        payload: dict[str, Any] = {}
        if credentials:
            payload["credentials"] = self._payload_factory.create_credentials(
                credentials
            )
        if storage:
            payload["storage"] = self._payload_factory.create_storage(storage)
        if registry:
            payload["registry"] = self._payload_factory.create_registry(registry)
        if orchestrator:
            payload["orchestrator"] = self._payload_factory.create_orchestrator(
                orchestrator
            )
        if monitoring:
            payload["monitoring"] = self._payload_factory.create_monitoring(monitoring)
        if secrets:
            payload["secrets"] = self._payload_factory.create_secrets(secrets)
        if metrics:
            payload["metrics"] = self._payload_factory.create_metrics(metrics)
        if disks:
            payload["disks"] = self._payload_factory.create_disks(disks)
        if buckets:
            payload["buckets"] = self._payload_factory.create_buckets(buckets)
        if ingress:
            payload["ingress"] = self._payload_factory.create_ingress(ingress)
        if dns:
            payload["dns"] = self._payload_factory.create_dns(dns)
        url = self._clusters_url / name
        async with self._client.patch(url, json=payload) as resp:
            resp.raise_for_status()
            resp_payload = await resp.json()
            return self._entity_factory.create_cluster(resp_payload)

    async def delete_cluster(self, name: str) -> None:
        assert self._client
        async with self._client.delete(self._clusters_url / name) as resp:
            resp.raise_for_status()

    async def add_storage(
        self,
        cluster_name: str,
        storage_name: str,
        size_mb: int | None = None,
        *,
        start_deployment: bool = True,
        ignore_existing: bool = False,
    ) -> Cluster:
        assert self._client
        try:
            url = self._clusters_url / cluster_name / "cloud_provider/storages"
            payload: dict[str, Any] = {"name": storage_name}
            if size_mb is not None:
                payload["size_mb"] = size_mb
            async with self._client.post(
                url.with_query(start_deployment=str(start_deployment).lower()),
                json=payload,
            ) as response:
                response.raise_for_status()
                resp_payload = await response.json()
                return self._entity_factory.create_cluster(resp_payload)
        except ClientResponseError as e:
            if not ignore_existing or e.status != 409:
                raise
        return await self.get_cluster(cluster_name)

    async def patch_storage(
        self,
        cluster_name: str,
        storage_name: str | None,
        ready: bool | None = None,
        *,
        ignore_not_found: bool = False,
    ) -> Cluster:
        assert self._client
        try:
            if storage_name:
                url = (
                    self._clusters_url
                    / cluster_name
                    / "cloud_provider/storages"
                    / storage_name
                )
            else:
                url = (
                    self._clusters_url
                    / cluster_name
                    / "cloud_provider/storages/default/entry"
                )
            payload: dict[str, Any] = {}
            if ready is not None:
                payload["ready"] = ready
            async with self._client.patch(url, json=payload) as response:
                response.raise_for_status()
                resp_payload = await response.json()
                return self._entity_factory.create_cluster(resp_payload)
        except ClientResponseError as e:
            if not ignore_not_found or e.status != 404:
                raise
        return await self.get_cluster(cluster_name)

    async def remove_storage(
        self,
        cluster_name: str,
        storage_name: str,
        *,
        start_deployment: bool = True,
        ignore_not_found: bool = False,
    ) -> Cluster:
        assert self._client
        try:
            url = (
                self._clusters_url
                / cluster_name
                / "cloud_provider/storages"
                / storage_name
            )
            async with self._client.delete(
                url.with_query(start_deployment=str(start_deployment).lower())
            ) as response:
                response.raise_for_status()
                resp_payload = await response.json()
                return self._entity_factory.create_cluster(resp_payload)
        except ClientResponseError as e:
            if not ignore_not_found or e.status != 404:
                raise
        return await self.get_cluster(cluster_name)
