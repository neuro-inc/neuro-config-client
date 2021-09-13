import logging
from types import TracebackType
from typing import Optional, Sequence, Type

import aiohttp
from yarl import URL

from .converters import PrimitiveToClusterConverter
from .models import Cluster


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
        self._client: Optional[aiohttp.ClientSession] = None
        self._primitive_to_cluster_converter = PrimitiveToClusterConverter()

    async def __aenter__(self) -> "ConfigClient":
        self._client = await self._create_http_client()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
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
        async with self._client.get(
            self._clusters_url, params={"include": "all"}
        ) as response:
            response.raise_for_status()
            payload = await response.json()
            return [
                self._primitive_to_cluster_converter.convert_cluster(p) for p in payload
            ]

    async def get_cluster(self, name: str) -> Cluster:
        assert self._client
        async with self._client.get(
            self._clusters_url / name, params={"include": "all"}
        ) as response:
            response.raise_for_status()
            payload = await response.json()
            return self._primitive_to_cluster_converter.convert_cluster(payload)
