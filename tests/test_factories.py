from __future__ import annotations

import sys
from datetime import datetime, time
from decimal import Decimal
from typing import Any
from unittest import mock

import pytest
from yarl import URL

from neuro_config_client.entities import (
    AMDGPU,
    AMDGPUPreset,
    AppsConfig,
    ARecord,
    BucketsConfig,
    DisksConfig,
    EnergyConfig,
    EnergySchedule,
    EnergySchedulePeriod,
    GrafanaConfig,
    IdleJobConfig,
    IntelGPU,
    IntelGPUPreset,
    MonitoringConfig,
    NvidiaGPU,
    NvidiaGPUPreset,
    OrchestratorConfig,
    PatchClusterRequest,
    PatchOrchestratorConfigRequest,
    PrometheusConfig,
    RegistryConfig,
    ResourcePoolType,
    ResourcePreset,
    Resources,
    SecretsConfig,
    StorageConfig,
    TPUPreset,
    TPUResource,
    VolumeConfig,
)
from neuro_config_client.factories import EntityFactory, PayloadFactory

if sys.version_info >= (3, 9):
    from zoneinfo import ZoneInfo
else:
    # why not backports.zoneinfo: https://github.com/pganssle/zoneinfo/issues/125
    from backports.zoneinfo._zoneinfo import ZoneInfo


@pytest.fixture()
def nvidia_small_gpu() -> str:
    return "nvidia-tesla-k80"


@pytest.fixture()
def amd_small_gpu() -> str:
    return "instinct-mi25"


@pytest.fixture()
def intel_small_gpu() -> str:
    return "flex-170"


class TestEntityFactory:
    @pytest.fixture
    def factory(self) -> EntityFactory:
        return EntityFactory()

    def test_create_cluster_defaults(self, factory: EntityFactory) -> None:
        result = factory.create_cluster(
            {
                "name": "default",
                "status": "blank",
                "orchestrator": {
                    "job_hostname_template": "{job_id}.jobs-dev.neu.ro",
                    "job_fallback_hostname": "default.jobs-dev.neu.ro",
                    "job_schedule_timeout_s": 1,
                    "job_schedule_scale_up_timeout_s": 2,
                    "is_http_ingress_secure": False,
                    "resource_pool_types": [{"name": "node-pool"}],
                },
                "storage": {"url": "https://storage-dev.neu.ro"},
                "registry": {
                    "url": "https://registry-dev.neu.ro",
                    "email": "dev@neu.ro",
                },
                "monitoring": {"url": "https://monitoring-dev.neu.ro"},
                "secrets": {"url": "https://secrets-dev.neu.ro"},
                "grafana": {"url": "https://grafana-dev.neu.ro"},
                "prometheus": {"url": "https://prometheus-dev.neu.ro"},
                "disks": {
                    "url": "https://disks-dev.neu.ro",
                    "storage_limit_per_user": 1024,
                },
                "buckets": {
                    "url": "https://buckets-dev.neu.ro",
                    "disable_creation": True,
                },
                "energy": {
                    "co2_grams_eq_per_kwh": 100,
                    "schedules": [
                        {"name": "default", "price_per_kwh": "123.4"},
                        {
                            "name": "green",
                            "price_per_kwh": "123.4",
                            "periods": [
                                {
                                    "weekday": 1,
                                    "start_time": "23:00",
                                    "end_time": "23:59",
                                }
                            ],
                        },
                    ],
                },
                "apps": {
                    "apps_hostname_templates": ["{app_name}.apps.default.org.neu.ro"],
                    "app_proxy_url": "outputs-proxy.apps.default.org.neu.ro",
                },
                "created_at": str(datetime.now()),
            }
        )

        assert result.name == "default"
        assert result.timezone == ZoneInfo("UTC")
        assert result.location is None
        assert result.logo_url is None
        assert result.orchestrator
        assert result.storage
        assert result.registry
        assert result.monitoring
        assert result.secrets
        assert result.grafana
        assert result.prometheus
        assert result.disks
        assert result.dns
        assert result.buckets
        assert result.energy
        assert result.apps
        assert result.created_at

    def test_create_cluster(self, factory: EntityFactory) -> None:
        result = factory.create_cluster(
            {
                "name": "default",
                "status": "blank",
                "location": "us",
                "logo_url": "https://logo",
                "timezone": "America/Los_Angeles",
                "orchestrator": {
                    "job_hostname_template": "{job_id}.jobs-dev.neu.ro",
                    "job_fallback_hostname": "default.jobs-dev.neu.ro",
                    "job_schedule_timeout_s": 1,
                    "job_schedule_scale_up_timeout_s": 2,
                    "is_http_ingress_secure": False,
                    "resource_pool_types": [{"name": "node-pool"}],
                },
                "storage": {"url": "https://storage-dev.neu.ro"},
                "registry": {
                    "url": "https://registry-dev.neu.ro",
                    "email": "dev@neu.ro",
                },
                "monitoring": {"url": "https://monitoring-dev.neu.ro"},
                "secrets": {"url": "https://secrets-dev.neu.ro"},
                "grafana": {"url": "https://grafana-dev.neu.ro"},
                "prometheus": {"url": "https://prometheus-dev.neu.ro"},
                "disks": {
                    "url": "https://disks-dev.neu.ro",
                    "storage_limit_per_user": 1024,
                },
                "buckets": {
                    "url": "https://buckets-dev.neu.ro",
                    "disable_creation": True,
                },
                "energy": {
                    "co2_grams_eq_per_kwh": 100,
                    "schedules": [
                        {"name": "default", "price_per_kwh": "123.4"},
                        {
                            "name": "green",
                            "price_per_kwh": "123.4",
                            "periods": [
                                {
                                    "weekday": 1,
                                    "start_time": "23:00",
                                    "end_time": "23:59",
                                }
                            ],
                        },
                    ],
                },
                "apps": {
                    "apps_hostname_templates": ["{app_name}.apps.default.org.neu.ro"],
                    "app_proxy_url": "outputs-proxy.apps.default.org.neu.ro",
                },
                "created_at": str(datetime.now()),
            }
        )

        assert result.name == "default"
        assert result.timezone == ZoneInfo("America/Los_Angeles")
        assert result.location == "us"
        assert result.logo_url == URL("https://logo")

    def test_create_cluster__invalid_timezone(self, factory: EntityFactory) -> None:
        with pytest.raises(ValueError, match="invalid timezone"):
            factory.create_cluster(
                {
                    "name": "default",
                    "status": "blank",
                    "created_at": str(datetime.now()),
                    "timezone": "invalid",
                }
            )

    def test_create_orchestrator(self, factory: EntityFactory) -> None:
        result = factory.create_orchestrator(
            {
                "job_hostname_template": "{job_id}.jobs-dev.neu.ro",
                "job_fallback_hostname": "default.jobs-dev.neu.ro",
                "job_schedule_timeout_s": 1,
                "job_schedule_scale_up_timeout_s": 2,
                "is_http_ingress_secure": False,
                "resource_pool_types": [{"name": "node-pool"}],
                "resource_presets": [
                    {
                        "name": "cpu-micro",
                        "credits_per_hour": "10",
                        "cpu": 0.1,
                        "memory": 100,
                    }
                ],
                "allow_privileged_mode": True,
                "allow_job_priority": True,
                "pre_pull_images": ["neuromation/base"],
                "idle_jobs": [
                    {
                        "name": "idle",
                        "count": 1,
                        "image": "miner",
                        "resources": {
                            "cpu": 1,
                            "memory": 1024,
                            "nvidia_gpu": 1,
                            "amd_gpu": 2,
                            "intel_gpu": 3,
                        },
                    },
                    {
                        "name": "idle",
                        "count": 1,
                        "image": "miner",
                        "command": ["bash"],
                        "args": ["-c", "sleep infinity"],
                        "resources": {"cpu": 1, "memory": 1024},
                        "env": {"NAME": "VALUE"},
                        "node_selector": {"label": "value"},
                        "image_pull_secret": "secret",
                    },
                ],
            }
        )

        assert result == OrchestratorConfig(
            job_hostname_template="{job_id}.jobs-dev.neu.ro",
            job_fallback_hostname="default.jobs-dev.neu.ro",
            job_schedule_timeout_s=1,
            job_schedule_scale_up_timeout_s=2,
            is_http_ingress_secure=False,
            resource_pool_types=[mock.ANY],
            resource_presets=[mock.ANY],
            allow_privileged_mode=True,
            allow_job_priority=True,
            pre_pull_images=["neuromation/base"],
            idle_jobs=[
                IdleJobConfig(
                    name="idle",
                    count=1,
                    image="miner",
                    resources=Resources(
                        cpu=1,
                        memory=1024,
                        nvidia_gpu=1,
                        amd_gpu=2,
                        intel_gpu=3,
                    ),
                ),
                IdleJobConfig(
                    name="idle",
                    count=1,
                    image="miner",
                    command=["bash"],
                    args=["-c", "sleep infinity"],
                    resources=Resources(cpu=1, memory=1024),
                    env={"NAME": "VALUE"},
                    node_selector={"label": "value"},
                    image_pull_secret="secret",
                ),
            ],
        )

    def test_create_orchestrator_default(self, factory: EntityFactory) -> None:
        result = factory.create_orchestrator(
            {
                "job_hostname_template": "{job_id}.jobs-dev.neu.ro",
                "job_fallback_hostname": "default.jobs-dev.neu.ro",
                "job_schedule_timeout_s": 1,
                "job_schedule_scale_up_timeout_s": 2,
                "is_http_ingress_secure": False,
            }
        )

        assert result == OrchestratorConfig(
            job_hostname_template="{job_id}.jobs-dev.neu.ro",
            job_fallback_hostname="default.jobs-dev.neu.ro",
            job_schedule_timeout_s=1,
            job_schedule_scale_up_timeout_s=2,
            is_http_ingress_secure=False,
            resource_pool_types=[],
            resource_presets=[],
            idle_jobs=[],
        )

    def test_create_resource_pool_type(
        self,
        factory: EntityFactory,
        nvidia_small_gpu: str,
        amd_small_gpu: str,
        intel_small_gpu: str,
    ) -> None:
        result = factory.create_resource_pool_type(
            {
                "name": "n1-highmem-4",
                "min_size": 1,
                "max_size": 2,
                "idle_size": 1,
                "cpu": 4.0,
                "available_cpu": 3.0,
                "memory": 12 * 1024,
                "available_memory": 10 * 1024,
                "disk_size": 700 * 2**30,
                "available_disk_size": 600 * 2**30,
                "nvidia_gpu": {
                    "count": 1,
                    "model": nvidia_small_gpu,
                    "memory": 123,
                },
                "nvidia_migs": {
                    "1g.5gb": {
                        "count": 7,
                        "model": f"{nvidia_small_gpu}-1g-5gb",
                        "memory": 456,
                    }
                },
                "amd_gpu": {
                    "count": 2,
                    "model": amd_small_gpu,
                },
                "intel_gpu": {
                    "count": 3,
                    "model": intel_small_gpu,
                },
                "tpu": {
                    "ipv4_cidr_block": "10.0.0.0/8",
                    "types": ["tpu"],
                    "software_versions": ["v1"],
                },
                "is_preemptible": True,
                "price": "1.0",
                "currency": "USD",
                "cpu_min_watts": 1.0,
                "cpu_max_watts": 2.0,
            }
        )

        assert result == ResourcePoolType(
            name="n1-highmem-4",
            min_size=1,
            max_size=2,
            idle_size=1,
            cpu=4.0,
            available_cpu=3.0,
            memory=12 * 1024,
            available_memory=10 * 1024,
            disk_size=700 * 2**30,
            available_disk_size=600 * 2**30,
            nvidia_gpu=NvidiaGPU(
                count=1,
                model=nvidia_small_gpu,
                memory=123,
            ),
            nvidia_migs={
                "1g.5gb": NvidiaGPU(
                    count=7,
                    model=f"{nvidia_small_gpu}-1g-5gb",
                    memory=456,
                )
            },
            amd_gpu=AMDGPU(count=2, model=amd_small_gpu),
            intel_gpu=IntelGPU(count=3, model=intel_small_gpu),
            tpu=mock.ANY,
            is_preemptible=True,
            price=Decimal("1.0"),
            currency="USD",
            cpu_min_watts=1.0,
            cpu_max_watts=2.0,
        )

    def test_create_empty_resource_pool_type(self, factory: EntityFactory) -> None:
        result = factory.create_resource_pool_type({"name": "node-pool"})

        assert result == ResourcePoolType(name="node-pool")

    def test_create_tpu_resource(self, factory: EntityFactory) -> None:
        result = factory.create_tpu_resource(
            {
                "ipv4_cidr_block": "10.0.0.0/8",
                "types": ["tpu"],
                "software_versions": ["v1"],
            }
        )

        assert result == TPUResource(
            ipv4_cidr_block="10.0.0.0/8", types=["tpu"], software_versions=["v1"]
        )

    def test_create_resource_preset_default(self, factory: EntityFactory) -> None:
        result = factory.create_resource_preset(
            {
                "name": "cpu-small",
                "credits_per_hour": "10",
                "cpu": 4.0,
                "memory": 1024,
            }
        )

        assert result == ResourcePreset(
            name="cpu-small", credits_per_hour=Decimal("10"), cpu=4.0, memory=1024
        )

    def test_create_resource_preset_custom(
        self,
        factory: EntityFactory,
        nvidia_small_gpu: str,
    ) -> None:
        result = factory.create_resource_preset(
            {
                "name": "gpu-small",
                "credits_per_hour": "10",
                "cpu": 4.0,
                "memory": 12288,
                "nvidia_gpu": {
                    "count": 1,
                    "model": nvidia_small_gpu,
                    "memory": 123,
                },
                "nvidia_migs": {
                    "1g.5gb": {
                        "count": 7,
                        "model": f"{nvidia_small_gpu}-1g-5gb",
                        "memory": 456,
                    }
                },
                "amd_gpu": {"count": 2},
                "intel_gpu": {"count": 3},
                "tpu": {"type": "tpu", "software_version": "v1"},
                "scheduler_enabled": True,
                "preemptible_node": True,
                "resource_pool_names": ["gpu"],
                "available_resource_pool_names": ["available-gpu"],
                "is_external_job": True,
            }
        )

        assert result == ResourcePreset(
            name="gpu-small",
            credits_per_hour=Decimal("10"),
            cpu=4.0,
            memory=12288,
            nvidia_gpu=NvidiaGPUPreset(
                count=1,
                model=nvidia_small_gpu,
                memory=123,
            ),
            nvidia_migs={
                "1g.5gb": NvidiaGPUPreset(
                    count=7,
                    model=f"{nvidia_small_gpu}-1g-5gb",
                    memory=456,
                )
            },
            amd_gpu=AMDGPUPreset(count=2),
            intel_gpu=IntelGPUPreset(count=3),
            tpu=TPUPreset(type="tpu", software_version="v1"),
            scheduler_enabled=True,
            preemptible_node=True,
            resource_pool_names=["gpu"],
            available_resource_pool_names=["available-gpu"],
            is_external_job=True,
        )

    def test_create_storage(self, factory: EntityFactory) -> None:
        result = factory.create_storage({"url": "https://storage-dev.neu.ro"})

        assert result == StorageConfig(
            url=URL("https://storage-dev.neu.ro"), volumes=[]
        )

    def test_create_storage_with_volumes(self, factory: EntityFactory) -> None:
        result = factory.create_storage(
            {
                "url": "https://storage-dev.neu.ro",
                "volumes": [
                    {"name": "test-1"},
                    {
                        "name": "test-2",
                        "path": "/volume",
                        "size": 1024,
                        "credits_per_hour_per_gb": "123",
                    },
                ],
            }
        )

        assert result == StorageConfig(
            url=URL("https://storage-dev.neu.ro"),
            volumes=[
                VolumeConfig(name="test-1"),
                VolumeConfig(
                    name="test-2",
                    path="/volume",
                    size=1024,
                    credits_per_hour_per_gb=Decimal(123),
                ),
            ],
        )

    def test_create_registry(self, factory: EntityFactory) -> None:
        result = factory.create_registry({"url": "https://registry-dev.neu.ro"})

        assert result == RegistryConfig(url=URL("https://registry-dev.neu.ro"))

    def test_create_monitoring(self, factory: EntityFactory) -> None:
        result = factory.create_monitoring({"url": "https://monitoring-dev.neu.ro"})

        assert result == MonitoringConfig(url=URL("https://monitoring-dev.neu.ro"))

    def test_create_secrets(self, factory: EntityFactory) -> None:
        result = factory.create_secrets({"url": "https://secrets-dev.neu.ro"})

        assert result == SecretsConfig(url=URL("https://secrets-dev.neu.ro"))

    def test_create_grafana(self, factory: EntityFactory) -> None:
        result = factory.create_grafana({"url": "https://grafana-dev.neu.ro"})

        assert result == GrafanaConfig(
            url=URL("https://grafana-dev.neu.ro"),
        )

    def test_create_prometheus(self, factory: EntityFactory) -> None:
        result = factory.create_prometheus({"url": "https://prometheus-dev.neu.ro"})

        assert result == PrometheusConfig(
            url=URL("https://prometheus-dev.neu.ro"),
        )
        result = factory.create_prometheus({"url": "https://grafana-dev.neu.ro"})

        assert result == PrometheusConfig(
            url=URL("https://prometheus-dev.neu.ro"),
        )

    def test_create_a_record_with_ips(self, factory: EntityFactory) -> None:
        result = factory.create_a_record(
            {"name": "*.jobs-dev.neu.ro.", "ips": ["192.168.0.2"]}
        )

        assert result == ARecord(name="*.jobs-dev.neu.ro.", ips=["192.168.0.2"])

    def test_create_a_record_dns_name(self, factory: EntityFactory) -> None:
        result = factory.create_a_record(
            {
                "name": "*.jobs-dev.neu.ro.",
                "dns_name": "load-balancer",
                "zone_id": "/hostedzone/1",
                "evaluate_target_health": True,
            }
        )

        assert result == ARecord(
            name="*.jobs-dev.neu.ro.",
            dns_name="load-balancer",
            zone_id="/hostedzone/1",
            evaluate_target_health=True,
        )

    def test_create_disks(self, factory: EntityFactory) -> None:
        result = factory.create_disks(
            {"url": "https://disks-dev.neu.ro", "storage_limit_per_user": 1024}
        )

        assert result == DisksConfig(
            url=URL("https://disks-dev.neu.ro"), storage_limit_per_user=1024
        )

    def test_create_buckets(self, factory: EntityFactory) -> None:
        result = factory.create_buckets(
            {"url": "https://buckets-dev.neu.ro", "disable_creation": True}
        )

        assert result == BucketsConfig(
            url=URL("https://buckets-dev.neu.ro"), disable_creation=True
        )

    def test_create_energy(self, factory: EntityFactory) -> None:
        timezone = ZoneInfo("America/Los_Angeles")
        energy = factory.create_energy(
            {
                "co2_grams_eq_per_kwh": 100,
                "schedules": [
                    {"name": "default", "price_per_kwh": "123.4"},
                    {
                        "name": "green",
                        "price_per_kwh": "123.4",
                        "periods": [
                            {"weekday": 1, "start_time": "23:00", "end_time": "23:59"}
                        ],
                    },
                ],
            },
            timezone=timezone,
        )

        assert energy == EnergyConfig(
            co2_grams_eq_per_kwh=100,
            schedules=[
                EnergySchedule(
                    name="default",
                    price_per_kwh=Decimal("123.4"),
                    periods=[],
                ),
                EnergySchedule(
                    name="green",
                    price_per_kwh=Decimal("123.4"),
                    periods=[
                        EnergySchedulePeriod(
                            weekday=1,
                            start_time=time(hour=23, minute=0, tzinfo=timezone),
                            end_time=time(hour=23, minute=59, tzinfo=timezone),
                        )
                    ],
                ),
            ],
        )

    @pytest.fixture
    def apps(self) -> AppsConfig:
        return AppsConfig(
            apps_hostname_templates=["{app_name}.apps.default.org.neu.ro"],
            app_proxy_url=URL("outputs-proxy.apps.default.org.neu.ro"),
        )

    @pytest.fixture
    def apps_dict(self) -> dict[str, Any]:
        return {
            "apps_hostname_templates": ["{app_name}.apps.default.org.neu.ro"],
            "app_proxy_url": "outputs-proxy.apps.default.org.neu.ro",
        }

    def test_create_apps(
        self, factory: EntityFactory, apps_dict: dict[str, Any], apps: AppsConfig
    ) -> None:
        result = factory.create_apps(apps_dict)
        assert result == apps


class TestPayloadFactory:
    @pytest.fixture
    def factory(self) -> PayloadFactory:
        return PayloadFactory()

    def test_create_patch_cluster_request(self, factory: PayloadFactory) -> None:
        result = factory.create_patch_cluster_request(
            PatchClusterRequest(
                location="us",
                logo_url=URL("https://logo"),
                storage=StorageConfig(url=URL("https://storage-dev.neu.ro")),
                registry=RegistryConfig(url=URL("https://registry-dev.neu.ro")),
                orchestrator=PatchOrchestratorConfigRequest(),
                monitoring=MonitoringConfig(url=URL("https://monitoring-dev.neu.ro")),
                secrets=SecretsConfig(url=URL("https://secrets-dev.neu.ro")),
                grafana=GrafanaConfig(
                    url=URL("https://grafana-dev.neu.ro"),
                ),
                prometheus=PrometheusConfig(
                    url=URL("https://prometheus-dev.neu.ro"),
                ),
                disks=DisksConfig(
                    url=URL("https://disks-dev.neu.ro"), storage_limit_per_user=1024
                ),
                buckets=BucketsConfig(
                    url=URL("https://buckets-dev.neu.ro"), disable_creation=True
                ),
                timezone=ZoneInfo("America/Los_Angeles"),
                energy=EnergyConfig(co2_grams_eq_per_kwh=100),
                apps=AppsConfig(
                    apps_hostname_templates=["{app_name}.apps.default.org.neu.ro"],
                    app_proxy_url=URL("outputs-proxy.apps.default.org.neu.ro"),
                ),
            )
        )

        assert result == {
            "location": "us",
            "logo_url": "https://logo",
            "storage": mock.ANY,
            "registry": mock.ANY,
            "orchestrator": mock.ANY,
            "monitoring": mock.ANY,
            "secrets": mock.ANY,
            "grafana": mock.ANY,
            "prometheus": mock.ANY,
            "disks": mock.ANY,
            "buckets": mock.ANY,
            "timezone": "America/Los_Angeles",
            "energy": mock.ANY,
            "apps": mock.ANY,
        }

    def test_create_patch_cluster_request_default(
        self, factory: PayloadFactory
    ) -> None:
        result = factory.create_patch_cluster_request(PatchClusterRequest())

        assert result == {}

    def test_create_orchestrator(self, factory: PayloadFactory) -> None:
        result = factory.create_orchestrator(
            OrchestratorConfig(
                job_hostname_template="{job_id}.jobs-dev.neu.ro",
                job_fallback_hostname="default.jobs-dev.neu.ro",
                job_schedule_timeout_s=1,
                job_schedule_scale_up_timeout_s=2,
                is_http_ingress_secure=False,
                allow_privileged_mode=True,
                allow_job_priority=True,
                resource_pool_types=[ResourcePoolType(name="cpu")],
                resource_presets=[
                    ResourcePreset(
                        name="cpu-micro",
                        credits_per_hour=Decimal(10),
                        cpu=0.1,
                        memory=100,
                    )
                ],
                pre_pull_images=["neuromation/base"],
                idle_jobs=[
                    IdleJobConfig(
                        name="idle",
                        count=1,
                        image="miner",
                        resources=Resources(
                            cpu=1,
                            memory=1024,
                            nvidia_gpu=1,
                            amd_gpu=2,
                            intel_gpu=3,
                        ),
                    ),
                    IdleJobConfig(
                        name="idle",
                        count=1,
                        image="miner",
                        command=["bash"],
                        args=["-c", "sleep infinity"],
                        resources=Resources(cpu=1, memory=1024),
                        env={"NAME": "VALUE"},
                        node_selector={"label": "value"},
                        image_pull_secret="secret",
                    ),
                ],
            )
        )

        assert result == {
            "job_hostname_template": "{job_id}.jobs-dev.neu.ro",
            "job_fallback_hostname": "default.jobs-dev.neu.ro",
            "job_schedule_timeout_s": 1,
            "job_schedule_scale_up_timeout_s": 2,
            "is_http_ingress_secure": False,
            "resource_pool_types": [mock.ANY],
            "resource_presets": [mock.ANY],
            "allow_privileged_mode": True,
            "allow_job_priority": True,
            "pre_pull_images": ["neuromation/base"],
            "idle_jobs": [
                {
                    "name": "idle",
                    "count": 1,
                    "image": "miner",
                    "resources": {
                        "cpu": 1,
                        "memory": 1024,
                        "nvidia_gpu": 1,
                        "amd_gpu": 2,
                        "intel_gpu": 3,
                    },
                },
                {
                    "name": "idle",
                    "count": 1,
                    "image": "miner",
                    "command": ["bash"],
                    "args": ["-c", "sleep infinity"],
                    "resources": {"cpu": 1, "memory": 1024},
                    "env": {"NAME": "VALUE"},
                    "node_selector": {"label": "value"},
                    "image_pull_secret": "secret",
                },
            ],
        }

    def test_create_orchestrator_default(self, factory: PayloadFactory) -> None:
        result = factory.create_orchestrator(
            OrchestratorConfig(
                job_hostname_template="{job_id}.jobs-dev.neu.ro",
                job_fallback_hostname="default.jobs-dev.neu.ro",
                job_schedule_timeout_s=1,
                job_schedule_scale_up_timeout_s=2,
                is_http_ingress_secure=False,
            )
        )

        assert result == {
            "job_hostname_template": "{job_id}.jobs-dev.neu.ro",
            "job_fallback_hostname": "default.jobs-dev.neu.ro",
            "job_schedule_timeout_s": 1,
            "job_schedule_scale_up_timeout_s": 2,
            "is_http_ingress_secure": False,
        }

    def test_create_patch_orchestrator_request(self, factory: PayloadFactory) -> None:
        result = factory.create_patch_orchestrator_request(
            PatchOrchestratorConfigRequest(
                job_hostname_template="{job_id}.jobs-dev.neu.ro",
                job_fallback_hostname="default.jobs-dev.neu.ro",
                job_schedule_timeout_s=1,
                job_schedule_scale_up_timeout_s=2,
                is_http_ingress_secure=False,
                allow_privileged_mode=True,
                allow_job_priority=True,
                resource_pool_types=[ResourcePoolType(name="cpu")],
                resource_presets=[
                    ResourcePreset(
                        name="cpu-micro",
                        credits_per_hour=Decimal(10),
                        cpu=0.1,
                        memory=100,
                    )
                ],
                pre_pull_images=["neuromation/base"],
                idle_jobs=[
                    IdleJobConfig(
                        name="idle",
                        count=1,
                        image="miner",
                        resources=Resources(cpu=1, memory=1024),
                    )
                ],
            )
        )

        assert result == {
            "job_hostname_template": "{job_id}.jobs-dev.neu.ro",
            "job_fallback_hostname": "default.jobs-dev.neu.ro",
            "job_schedule_timeout_s": 1,
            "job_schedule_scale_up_timeout_s": 2,
            "is_http_ingress_secure": False,
            "resource_pool_types": [mock.ANY],
            "resource_presets": [mock.ANY],
            "allow_privileged_mode": True,
            "allow_job_priority": True,
            "pre_pull_images": ["neuromation/base"],
            "idle_jobs": [
                {
                    "name": "idle",
                    "count": 1,
                    "image": "miner",
                    "resources": {"cpu": 1, "memory": 1024},
                }
            ],
        }

    def test_create_patch_orchestrator_request_default(
        self, factory: PayloadFactory
    ) -> None:
        result = factory.create_patch_orchestrator_request(
            PatchOrchestratorConfigRequest()
        )

        assert result == {}

    def test_create_resource_pool_type(
        self,
        factory: PayloadFactory,
        nvidia_small_gpu: str,
        amd_small_gpu: str,
        intel_small_gpu: str,
    ) -> None:
        result = factory.create_resource_pool_type(
            ResourcePoolType(
                name="n1-highmem-4",
                min_size=1,
                max_size=2,
                idle_size=1,
                cpu=4.0,
                available_cpu=3.0,
                memory=12 * 1024,
                available_memory=10 * 1024,
                disk_size=700,
                available_disk_size=670,
                nvidia_gpu=NvidiaGPU(
                    count=1,
                    model=nvidia_small_gpu,
                    memory=123,
                ),
                nvidia_migs={
                    "1g.5gb": NvidiaGPU(
                        count=7,
                        model=f"{nvidia_small_gpu}-1g-5gb",
                        memory=456,
                    )
                },
                amd_gpu=AMDGPU(count=2, model=amd_small_gpu),
                intel_gpu=IntelGPU(count=3, model=intel_small_gpu),
                tpu=TPUResource(
                    ipv4_cidr_block="10.0.0.0/8",
                    types=["tpu"],
                    software_versions=["v1"],
                ),
                is_preemptible=True,
                price=Decimal("1.0"),
                currency="USD",
                cpu_min_watts=1.0,
                cpu_max_watts=2.0,
            )
        )

        assert result == {
            "name": "n1-highmem-4",
            "min_size": 1,
            "max_size": 2,
            "idle_size": 1,
            "cpu": 4.0,
            "available_cpu": 3.0,
            "memory": 12 * 1024,
            "available_memory": 10 * 1024,
            "disk_size": 700,
            "available_disk_size": 670,
            "nvidia_gpu": {
                "count": 1,
                "model": nvidia_small_gpu,
                "memory": 123,
            },
            "nvidia_migs": {
                "1g.5gb": {
                    "count": 7,
                    "model": f"{nvidia_small_gpu}-1g-5gb",
                    "memory": 456,
                }
            },
            "amd_gpu": {
                "count": 2,
                "model": amd_small_gpu,
            },
            "intel_gpu": {
                "count": 3,
                "model": intel_small_gpu,
            },
            "tpu": {
                "ipv4_cidr_block": "10.0.0.0/8",
                "types": ["tpu"],
                "software_versions": ["v1"],
            },
            "is_preemptible": True,
            "price": "1.0",
            "currency": "USD",
            "cpu_min_watts": 1.0,
            "cpu_max_watts": 2.0,
        }

    def test_create_empty_resource_pool_type(self, factory: PayloadFactory) -> None:
        result = factory.create_resource_pool_type(ResourcePoolType(name="node-pool"))

        assert result == {
            "name": "node-pool",
            "cpu": 1.0,
            "available_cpu": 1.0,
            "memory": 2**30,
            "available_memory": 2**30,
            "disk_size": 150 * 2**30,
            "available_disk_size": 150 * 2**30,
            "idle_size": 0,
            "is_preemptible": False,
            "min_size": 0,
            "max_size": 1,
        }

    def test_create_tpu_resource(self, factory: PayloadFactory) -> None:
        result = factory.create_tpu_resource(
            TPUResource(
                ipv4_cidr_block="10.0.0.0/8", types=["tpu"], software_versions=["v1"]
            )
        )

        assert result == {
            "ipv4_cidr_block": "10.0.0.0/8",
            "types": ["tpu"],
            "software_versions": ["v1"],
        }

    def test_create_resource_preset(self, factory: PayloadFactory) -> None:
        result = factory.create_resource_preset(
            ResourcePreset(
                name="cpu-small",
                credits_per_hour=Decimal("10"),
                cpu=4.0,
                memory=1024,
            )
        )

        assert result == {
            "name": "cpu-small",
            "credits_per_hour": "10",
            "cpu": 4.0,
            "memory": 1024,
        }

    def test_create_resource_preset_custom(
        self,
        factory: PayloadFactory,
        nvidia_small_gpu: str,
        amd_small_gpu: str,
    ) -> None:
        result = factory.create_resource_preset(
            ResourcePreset(
                name="gpu-small",
                credits_per_hour=Decimal("10"),
                cpu=4.0,
                memory=12288,
                nvidia_gpu=NvidiaGPUPreset(count=1, model=nvidia_small_gpu, memory=123),
                nvidia_migs={
                    "1g.5gb": NvidiaGPUPreset(
                        count=7,
                        model=f"{nvidia_small_gpu}-1g-5gb",
                        memory=456,
                    )
                },
                amd_gpu=AMDGPUPreset(count=2, model=amd_small_gpu),
                intel_gpu=IntelGPUPreset(count=3),
                tpu=TPUPreset(type="tpu", software_version="v1"),
                scheduler_enabled=True,
                preemptible_node=True,
                resource_pool_names=["gpu"],
            )
        )

        assert result == {
            "name": "gpu-small",
            "credits_per_hour": "10",
            "cpu": 4.0,
            "memory": 12288,
            "nvidia_gpu": {
                "count": 1,
                "model": nvidia_small_gpu,
            },
            "nvidia_migs": {
                "1g.5gb": {
                    "count": 7,
                    "model": f"{nvidia_small_gpu}-1g-5gb",
                }
            },
            "amd_gpu": {"count": 2, "model": amd_small_gpu},
            "intel_gpu": {"count": 3},
            "tpu": {"type": "tpu", "software_version": "v1"},
            "scheduler_enabled": True,
            "preemptible_node": True,
            "resource_pool_names": ["gpu"],
        }

    def test_create_storage(self, factory: PayloadFactory) -> None:
        result = factory.create_storage(
            StorageConfig(url=URL("https://storage-dev.neu.ro"))
        )

        assert result == {"url": "https://storage-dev.neu.ro"}

    def test_create_storage_with_volumes(self, factory: PayloadFactory) -> None:
        result = factory.create_storage(
            StorageConfig(
                url=URL("https://storage-dev.neu.ro"),
                volumes=[
                    VolumeConfig(name="test-1"),
                    VolumeConfig(
                        name="test-2",
                        path="/volume",
                        size=1024,
                        credits_per_hour_per_gb=Decimal(123),
                    ),
                ],
            )
        )

        assert result == {
            "url": "https://storage-dev.neu.ro",
            "volumes": [
                {
                    "name": "test-1",
                    "credits_per_hour_per_gb": "0",
                },
                {
                    "name": "test-2",
                    "path": "/volume",
                    "size": 1024,
                    "credits_per_hour_per_gb": "123",
                },
            ],
        }

    def test_create_registry(self, factory: PayloadFactory) -> None:
        result = factory.create_registry(
            RegistryConfig(url=URL("https://registry-dev.neu.ro"))
        )

        assert result == {"url": "https://registry-dev.neu.ro"}

    def test_create_monitoring(self, factory: PayloadFactory) -> None:
        result = factory.create_monitoring(
            MonitoringConfig(url=URL("https://monitoring-dev.neu.ro"))
        )

        assert result == {"url": "https://monitoring-dev.neu.ro"}

    def test_create_secrets(self, factory: PayloadFactory) -> None:
        result = factory.create_secrets(
            SecretsConfig(url=URL("https://secrets-dev.neu.ro"))
        )

        assert result == {"url": "https://secrets-dev.neu.ro"}

    def test_create_grafana(self, factory: PayloadFactory) -> None:
        result = factory.create_grafana(
            GrafanaConfig(
                url=URL("https://grafana-dev.neu.ro"),
            )
        )

        assert result == {
            "url": "https://grafana-dev.neu.ro",
        }

    def test_create_prometheus(self, factory: PayloadFactory) -> None:
        result = factory.create_prometheus(
            PrometheusConfig(
                url=URL("https://prometheus-dev.neu.ro"),
            )
        )

        assert result == {
            "url": "https://prometheus-dev.neu.ro",
        }

    def test_create_a_record_with_ips(self, factory: PayloadFactory) -> None:
        result = factory.create_a_record(
            ARecord(name="*.jobs-dev.neu.ro.", ips=["192.168.0.2"])
        )

        assert result == {"name": "*.jobs-dev.neu.ro.", "ips": ["192.168.0.2"]}

    def test_create_a_record_dns_name(self, factory: PayloadFactory) -> None:
        result = factory.create_a_record(
            ARecord(
                name="*.jobs-dev.neu.ro.",
                dns_name="load-balancer",
                zone_id="/hostedzone/1",
                evaluate_target_health=True,
            )
        )

        assert result == {
            "name": "*.jobs-dev.neu.ro.",
            "dns_name": "load-balancer",
            "zone_id": "/hostedzone/1",
            "evaluate_target_health": True,
        }

    def test_create_disks(self, factory: PayloadFactory) -> None:
        result = factory.create_disks(
            DisksConfig(
                url=URL("https://disks-dev.neu.ro"), storage_limit_per_user=1024
            )
        )

        assert result == {
            "url": "https://disks-dev.neu.ro",
            "storage_limit_per_user": 1024,
        }

    def test_create_buckets(self, factory: PayloadFactory) -> None:
        result = factory.create_buckets(
            BucketsConfig(url=URL("https://buckets-dev.neu.ro"), disable_creation=True)
        )

        assert result == {"url": "https://buckets-dev.neu.ro", "disable_creation": True}

    def test_create_energy(self, factory: PayloadFactory) -> None:
        timezone = ZoneInfo("America/Los_Angeles")
        energy = factory.create_energy(
            EnergyConfig(
                co2_grams_eq_per_kwh=100,
                schedules=[
                    EnergySchedule(name="default", price_per_kwh=Decimal("246.8")),
                    EnergySchedule(
                        name="green",
                        price_per_kwh=Decimal("123.4"),
                        periods=[
                            EnergySchedulePeriod(
                                weekday=1,
                                start_time=time(hour=23, minute=0, tzinfo=timezone),
                                end_time=time(hour=0, minute=0, tzinfo=timezone),
                            )
                        ],
                    ),
                ],
            )
        )

        assert energy == {
            "co2_grams_eq_per_kwh": 100,
            "schedules": [
                {"name": "default", "price_per_kwh": "246.8"},
                {
                    "name": "green",
                    "price_per_kwh": "123.4",
                    "periods": [
                        {"weekday": 1, "start_time": "23:00", "end_time": "00:00"}
                    ],
                },
            ],
        }

    @pytest.fixture
    def apps(self) -> AppsConfig:
        return AppsConfig(
            apps_hostname_templates=["{app_name}.apps.default.org.neu.ro"],
            app_proxy_url=URL("outputs-proxy.apps.default.org.neu.ro"),
        )

    def test_create_apps(self, factory: PayloadFactory, apps: AppsConfig) -> None:
        result = factory.create_apps(apps)
        assert result == {
            "apps_hostname_templates": ["{app_name}.apps.default.org.neu.ro"],
            "app_proxy_url": "outputs-proxy.apps.default.org.neu.ro",
        }
