from __future__ import annotations

import logging
from collections.abc import Sequence
from decimal import Decimal
from types import TracebackType
from typing import Any

import aiohttp
from aiohttp import ClientResponseError
from yarl import URL

from .entities import (
    BucketsConfig,
    CloudProviderType,
    Cluster,
    CredentialsConfig,
    DisksConfig,
    DNSConfig,
    IngressConfig,
    MetricsConfig,
    MonitoringConfig,
    NodePool,
    NodePoolTemplate,
    NodeRole,
    NotificationType,
    OrchestratorConfig,
    RegistryConfig,
    SecretsConfig,
    StorageConfig,
    TemplateNotFoundException,
)
from .factories import EntityFactory, PayloadFactory

logger = logging.getLogger(__name__)


class ConfigClient:
    def __init__(
        self,
        url: URL,
        token: str | None = None,
        timeout: aiohttp.ClientTimeout = aiohttp.client.DEFAULT_TIMEOUT,
        trace_configs: Sequence[aiohttp.TraceConfig] = (),
    ):
        self._clusters_url = url / "api/v1/clusters"
        self._cloud_providers_url = url / "api/v1/cloud_providers"
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
            timeout=self._timeout,
            trace_configs=list(self._trace_configs),
        )
        return await client.__aenter__()

    def _create_headers(self, *, token: str | None = None) -> dict[str, str]:
        result = {}
        token = token or self._token
        if token:
            result["Authorization"] = f"Bearer {token}"
        return result

    async def get_clusters(self, *, token: str | None = None) -> Sequence[Cluster]:
        assert self._client
        headers = self._create_headers(token=token)
        async with self._client.get(self._clusters_url, headers=headers) as response:
            response.raise_for_status()
            payload = await response.json()
            return [self._entity_factory.create_cluster(p) for p in payload]

    async def get_cluster(self, name: str, *, token: str | None = None) -> Cluster:
        assert self._client
        headers = self._create_headers(token=token)
        async with self._client.get(
            self._clusters_url / name, headers=headers
        ) as response:
            response.raise_for_status()
            payload = await response.json()
            return self._entity_factory.create_cluster(payload)

    async def create_blank_cluster(
        self,
        name: str,
        service_token: str,
        *,
        token: str | None = None,
        ignore_existing: bool = False,
    ) -> Cluster:
        assert self._client
        headers = self._create_headers(token=token)
        payload = {"name": name, "token": service_token}
        try:
            async with self._client.post(
                self._clusters_url, headers=headers, json=payload
            ) as resp:
                resp.raise_for_status()
                resp_payload = await resp.json()
                return self._entity_factory.create_cluster(resp_payload)
        except ClientResponseError as e:
            is_existing = e.status == 400 and "already exists" in e.message
            if not ignore_existing or is_existing:
                raise
        return await self.get_cluster(name)

    async def patch_cluster(
        self,
        name: str,
        *,
        token: str | None = None,
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
        url = self._clusters_url / name
        headers = self._create_headers(token=token)
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
        async with self._client.patch(url, headers=headers, json=payload) as resp:
            resp.raise_for_status()
            resp_payload = await resp.json()
            return self._entity_factory.create_cluster(resp_payload)

    async def delete_cluster(self, name: str, *, token: str | None = None) -> None:
        assert self._client
        headers = self._create_headers(token=token)
        async with self._client.delete(
            self._clusters_url / name, headers=headers
        ) as resp:
            resp.raise_for_status()

    async def add_storage(
        self,
        cluster_name: str,
        storage_name: str,
        size_mb: int | None = None,
        *,
        token: str | None = None,
        start_deployment: bool = True,
        ignore_existing: bool = False,
    ) -> Cluster:
        assert self._client
        try:
            url = self._clusters_url / cluster_name / "cloud_provider/storages"
            headers = self._create_headers(token=token)
            payload: dict[str, Any] = {"name": storage_name}
            if size_mb is not None:
                payload["size_mb"] = size_mb
            async with self._client.post(
                url.with_query(start_deployment=str(start_deployment).lower()),
                headers=headers,
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
        token: str | None = None,
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
            headers = self._create_headers(token=token)
            payload: dict[str, Any] = {}
            if ready is not None:
                payload["ready"] = ready
            async with self._client.patch(
                url, headers=headers, json=payload
            ) as response:
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
        token: str | None = None,
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
            headers = self._create_headers(token=token)
            async with self._client.delete(
                url.with_query(start_deployment=str(start_deployment).lower()),
                headers=headers,
            ) as response:
                response.raise_for_status()
                resp_payload = await response.json()
                return self._entity_factory.create_cluster(resp_payload)
        except ClientResponseError as e:
            if not ignore_not_found or e.status != 404:
                raise
        return await self.get_cluster(cluster_name)

    async def get_node_pool(
        self,
        cluster_name: str,
        node_pool_name: str,
        *,
        token: str | None = None,
    ) -> NodePool:
        assert self._client
        url = (
            self._clusters_url
            / cluster_name
            / "cloud_provider"
            / "node_pools"
            / node_pool_name
        )

        headers = self._create_headers(token=token)
        async with self._client.get(url=url, headers=headers) as response:
            response.raise_for_status()
            resp_payload = await response.json()
            return self._entity_factory.create_node_pool(resp_payload)

    async def get_node_pools(
        self,
        cluster_name: str,
        *,
        token: str | None = None,
    ) -> list[NodePool]:
        assert self._client
        url = self._clusters_url / cluster_name / "cloud_provider/node_pools"

        headers = self._create_headers(token=token)
        async with self._client.get(url=url, headers=headers) as response:
            response.raise_for_status()
            resp_payload = await response.json()
            return [self._entity_factory.create_node_pool(n) for n in resp_payload]

    async def get_node_pool_templates(
        self,
        cloud_provider_type: CloudProviderType,
        *,
        token: str | None = None,
    ) -> list[NodePoolTemplate]:
        assert self._client

        url = self._cloud_providers_url / cloud_provider_type.value
        headers = self._create_headers(token=token)
        async with self._client.get(url=url, headers=headers) as response:
            response.raise_for_status()
            resp_payload = await response.json()
            np_templates = [
                self._entity_factory.create_node_pool_template(npt)
                for npt in resp_payload["node_pools"]
            ]
            return np_templates

    async def add_node_pool(
        self,
        cluster_name: str,
        node_pool: NodePool,
        *,
        token: str | None = None,
        start_deployment: bool = True,
    ) -> Cluster:
        """Add new node pool to the existing cluster.
        Cloud provider should be already set up.

        Make sure you use one of the available node pool templates,
            if the cluster is deployed in public cloud (AWS / GCP / Azure / VCD).

        Args:
            cluster_name (str): Name of the cluster within the platform.
            node_pool (NodePool): Node pool instance.
                For templates, you could use template.to_node_pool() method
            token (str | None, optional): User token to perform changes.
                Should has write access to cluster://{cluster_name}/cloud_provider role.
            start_deployment (bool, optional): Start applying changes. Defaults to True.

        Returns:
            Cluster: Cluster instance with applied changes
        """
        assert self._client

        cluster = await self.get_cluster(cluster_name, token=token)
        assert cluster.cloud_provider
        if cluster.cloud_provider.type == CloudProviderType.ON_PREM:
            return await self._add_onprem_node_pool(
                cluster,
                node_pool,
                token=token,
                start_deployment=start_deployment,
            )
        else:
            return await self._add_cloud_node_pool(
                cluster,
                node_pool,
                token=token,
                start_deployment=start_deployment,
            )

    async def _add_onprem_node_pool(
        self,
        cluster: Cluster,
        node_pool: NodePool,
        token: str | None = None,
        start_deployment: bool = True,
    ) -> Cluster:
        assert self._client
        assert cluster.cloud_provider

        url = self._clusters_url / cluster.name / "cloud_provider/node_pools"
        headers = self._create_headers(token=token)
        payload = self._payload_factory.create_node_pool(
            node_pool, cluster.cloud_provider.type
        )
        async with self._client.post(
            url.with_query(start_deployment=str(start_deployment).lower()),
            headers=headers,
            json=payload,
        ) as response:
            response.raise_for_status()
            resp_payload = await response.json()
            return self._entity_factory.create_cluster(resp_payload)

    async def _add_cloud_node_pool(
        self,
        cluster: Cluster,
        node_pool: NodePool,
        *,
        token: str | None = None,
        start_deployment: bool = True,
    ) -> Cluster:
        assert self._client
        assert cluster.cloud_provider
        assert node_pool.id

        np_templates = await self.get_node_pool_templates(
            cluster.cloud_provider.type, token=token
        )
        assert np_templates, f"Node pool templates not found in cluster {cluster.name}"

        for np_template in np_templates:
            if np_template.id == node_pool.id:
                logger.info(f"Applying node pool template {np_template}")
                break
        else:
            logger.error(
                f"Node pool template {node_pool.id} is not available"
                f" in cluster {cluster.name}. "
                "Consider using one of the following: "
                f"{', '.join(np.id for np in np_templates)}"
            )
            raise TemplateNotFoundException.create(node_pool.id)

        node_pool = NodePool(
            name=node_pool.name or np_template.id,
            role=node_pool.role,
            min_size=node_pool.min_size,
            max_size=node_pool.max_size,
            idle_size=node_pool.idle_size,
            machine_type=np_template.machine_type,
            cpu=np_template.cpu,
            available_cpu=np_template.available_cpu,
            memory_mb=np_template.memory_mb,
            available_memory_mb=np_template.available_memory_mb,
            disk_size_gb=node_pool.disk_size_gb,
            disk_type=node_pool.disk_type,
            gpu=np_template.gpu or node_pool.gpu,
            gpu_model=np_template.gpu_model or node_pool.gpu_model,
            price=node_pool.price,
            currency=node_pool.currency,
            is_preemptible=node_pool.is_preemptible,
            zones=node_pool.zones,
        )

        url = self._clusters_url / cluster.name / "cloud_provider/node_pools"
        headers = self._create_headers(token=token)
        payload = self._payload_factory.create_node_pool(
            node_pool=node_pool,
            cloud_provider_type=cluster.cloud_provider.type,
        )

        async with self._client.post(
            url.with_query(start_deployment=str(start_deployment).lower()),
            headers=headers,
            json=payload,
        ) as response:
            response.raise_for_status()
            resp_payload = await response.json()
            return self._entity_factory.create_cluster(resp_payload)

    async def put_node_pool(
        self,
        cluster_name: str,
        node_pool_name: str,
        *,
        role: NodeRole | None = None,
        min_size: int | None = None,
        max_size: int | None = None,
        idle_size: int | None = None,
        machine_type: str | None = None,
        cpu: float | None = None,
        available_cpu: float | None = None,
        memory_mb: int | None = None,
        available_memorty_mb: int | None = None,
        disk_size_gb: int | None = None,
        disk_type: str | None = None,
        gpu: int | None = None,
        gpu_model: str | None = None,
        price: Decimal | None = None,
        currency: str | None = None,
        is_preemptible: bool | None = None,
        zones: tuple[str] | None = None,
        token: str | None = None,
        start_deployment: bool = True,
    ) -> Cluster:
        assert self._client

        current_np = await self.get_node_pool(cluster_name, node_pool_name, token=token)
        cluster = await self.get_cluster(cluster_name, token=token)
        assert cluster.cloud_provider

        new_np = NodePool(
            name=node_pool_name,
            role=role or current_np.role,
            min_size=min_size or current_np.min_size,
            max_size=max_size or current_np.max_size,
            idle_size=idle_size or current_np.idle_size,
            machine_type=machine_type or current_np.machine_type,
            cpu=cpu or current_np.cpu,
            available_cpu=available_cpu or current_np.available_cpu,
            memory_mb=memory_mb or current_np.memory_mb,
            available_memory_mb=available_memorty_mb or current_np.available_memory_mb,
            disk_size_gb=disk_size_gb or current_np.disk_size_gb,
            disk_type=disk_type or current_np.disk_type,
            gpu=gpu or current_np.gpu,
            gpu_model=gpu_model or current_np.gpu_model,
            price=price or current_np.price,
            currency=currency or current_np.currency,
            is_preemptible=is_preemptible or current_np.is_preemptible,
            zones=zones or current_np.zones,
        )

        url = (
            self._clusters_url
            / cluster_name
            / "cloud_provider"
            / "node_pools"
            / node_pool_name
        )
        headers = self._create_headers(token=token)
        payload = self._payload_factory.create_node_pool(
            new_np,
            cloud_provider_type=cluster.cloud_provider.type,
        )
        async with self._client.put(
            url.with_query(start_deployment=str(start_deployment).lower()),
            headers=headers,
            json=payload,
        ) as response:
            response.raise_for_status()
            resp_payload = await response.json()
            return self._entity_factory.create_cluster(resp_payload)

    async def delete_node_pool(
        self,
        cluster_name: str,
        node_pool_name: str,
        *,
        token: str | None = None,
        start_deployment: bool = True,
    ) -> Cluster:
        assert self._client

        url = (
            self._clusters_url
            / cluster_name
            / "cloud_provider/node_pools"
            / node_pool_name
        )
        headers = self._create_headers(token=token)
        async with self._client.delete(
            url.with_query(start_deployment=str(start_deployment).lower()),
            headers=headers,
        ) as response:
            response.raise_for_status()
            resp_payload = await response.json()
            return self._entity_factory.create_cluster(resp_payload)

    async def notify(
        self,
        cluster_name: str,
        notification_type: NotificationType,
        message: str | None = None,
        *,
        token: str | None = None,
    ) -> None:
        assert self._client
        url = self._clusters_url / cluster_name / "notifications"
        headers = self._create_headers(token=token)
        payload = {"notification_type": notification_type.value}
        if message:
            payload["message"] = message
        async with self._client.post(url, headers=headers, json=payload) as response:
            response.raise_for_status()
