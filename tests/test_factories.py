from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from typing import Any
from unittest import mock

import pytest
from yarl import URL

from neuro_config_client.entities import (
    ACMEEnvironment,
    ARecord,
    AWSCloudProvider,
    AWSCredentials,
    AWSStorage,
    AzureCloudProvider,
    AzureCredentials,
    AzureReplicationType,
    AzureStorage,
    AzureStorageTier,
    BucketsConfig,
    CloudProviderType,
    Cluster,
    ClusterLocationType,
    ClusterStatus,
    CredentialsConfig,
    DisksConfig,
    DNSConfig,
    DockerRegistryConfig,
    EFSPerformanceMode,
    EFSThroughputMode,
    EMCECSCredentials,
    GoogleCloudProvider,
    GoogleFilestoreTier,
    GoogleStorage,
    GrafanaCredentials,
    HelmRegistryConfig,
    IdleJobConfig,
    IngressConfig,
    KubernetesCredentials,
    MetricsConfig,
    MinioCredentials,
    MonitoringConfig,
    NeuroAuthConfig,
    NodePool,
    OnPremCloudProvider,
    OpenStackCredentials,
    OrchestratorConfig,
    RegistryConfig,
    ResourcePoolType,
    ResourcePreset,
    Resources,
    SecretsConfig,
    SentryCredentials,
    StorageConfig,
    StorageInstance,
    TPUPreset,
    TPUResource,
    VCDCloudProvider,
    VCDCredentials,
    VCDStorage,
    VolumeConfig,
)
from neuro_config_client.factories import EntityFactory, PayloadFactory


class TestEntityFactory:
    @pytest.fixture
    def factory(self) -> EntityFactory:
        return EntityFactory()

    def test_create_empty_cluster(self, factory: EntityFactory) -> None:
        result = factory.create_cluster(
            {"name": "default", "status": "blank", "created_at": str(datetime.now())}
        )

        assert result == Cluster(
            name="default", status=ClusterStatus.BLANK, created_at=mock.ANY
        )

    def test_create_cluster(
        self,
        factory: EntityFactory,
        google_cloud_provider_response: dict[str, Any],
        credentials: dict[str, Any],
    ) -> None:
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
                    "allow_privileged_mode": False,
                },
                "storage": {"url": "https://storage-dev.neu.ro"},
                "registry": {
                    "url": "https://registry-dev.neu.ro",
                    "email": "dev@neu.ro",
                },
                "monitoring": {"url": "https://monitoring-dev.neu.ro"},
                "secrets": {"url": "https://secrets-dev.neu.ro"},
                "metrics": {"url": "https://secrets-dev.neu.ro"},
                "disks": {
                    "url": "https://secrets-dev.neu.ro",
                    "storage_limit_per_user_gb": 1024,
                },
                "ingress": {"acme_environment": "production"},
                "dns": {
                    "name": "neu.ro",
                    "a_records": [
                        {"name": "*.jobs-dev.neu.ro.", "ips": ["192.168.0.2"]}
                    ],
                },
                "cloud_provider": google_cloud_provider_response,
                "credentials": credentials,
                "created_at": str(datetime.now()),
            }
        )

        assert result.name == "default"
        assert result.status == ClusterStatus.BLANK
        assert result.orchestrator
        assert result.storage
        assert result.registry
        assert result.monitoring
        assert result.secrets
        assert result.metrics
        assert result.disks
        assert result.ingress
        assert result.dns
        assert result.cloud_provider
        assert result.credentials
        assert result.created_at

    def test_create_orchestrator(self, factory: EntityFactory) -> None:
        result = factory.create_orchestrator(
            {
                "job_hostname_template": "{job_id}.jobs-dev.neu.ro",
                "job_internal_hostname_template": "{job_id}.platform-jobs",
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
                        "memory_mb": 100,
                    }
                ],
                "allow_privileged_mode": False,
                "pre_pull_images": ["neuromation/base"],
                "idle_jobs": [
                    {
                        "name": "idle",
                        "count": 1,
                        "image": "miner",
                        "resources": {"cpu_m": 1000, "memory_mb": 1024},
                    }
                ],
            }
        )

        assert result == OrchestratorConfig(
            job_hostname_template="{job_id}.jobs-dev.neu.ro",
            job_internal_hostname_template="{job_id}.platform-jobs",
            job_fallback_hostname="default.jobs-dev.neu.ro",
            job_schedule_timeout_s=1,
            job_schedule_scale_up_timeout_s=2,
            is_http_ingress_secure=False,
            resource_pool_types=[mock.ANY],
            resource_presets=[mock.ANY],
            allow_privileged_mode=False,
            pre_pull_images=["neuromation/base"],
            idle_jobs=[
                IdleJobConfig(
                    name="idle",
                    count=1,
                    image="miner",
                    resources=Resources(cpu_m=1000, memory_mb=1024),
                )
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
                "allow_privileged_mode": False,
            }
        )

        assert result == OrchestratorConfig(
            job_hostname_template="{job_id}.jobs-dev.neu.ro",
            job_internal_hostname_template=None,
            job_fallback_hostname="default.jobs-dev.neu.ro",
            job_schedule_timeout_s=1,
            job_schedule_scale_up_timeout_s=2,
            is_http_ingress_secure=False,
            allow_privileged_mode=False,
            resource_pool_types=[],
            resource_presets=[],
            idle_jobs=[],
        )

    def test_create_resource_pool_type(self, factory: EntityFactory) -> None:
        result = factory.create_resource_pool_type(
            {
                "name": "n1-highmem-4",
                "min_size": 1,
                "max_size": 2,
                "idle_size": 1,
                "cpu": 4.0,
                "available_cpu": 3.0,
                "memory_mb": 12 * 1024,
                "available_memory_mb": 10 * 1024,
                "disk_size_gb": 700,
                "gpu": 1,
                "gpu_model": "nvidia-tesla-k80",
                "tpu": {
                    "ipv4_cidr_block": "10.0.0.0/8",
                    "types": ["tpu"],
                    "software_versions": ["v1"],
                },
                "is_preemptible": True,
                "price": "1.0",
                "currency": "USD",
            }
        )

        assert result == ResourcePoolType(
            name="n1-highmem-4",
            min_size=1,
            max_size=2,
            idle_size=1,
            cpu=4.0,
            available_cpu=3.0,
            memory_mb=12 * 1024,
            available_memory_mb=10 * 1024,
            gpu=1,
            gpu_model="nvidia-tesla-k80",
            tpu=mock.ANY,
            is_preemptible=True,
            price=Decimal("1.0"),
            currency="USD",
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

    def test_create_resource_preset(self, factory: EntityFactory) -> None:
        result = factory.create_resource_preset(
            {
                "name": "cpu-small",
                "credits_per_hour": "10",
                "cpu": 4.0,
                "memory_mb": 1024,
            }
        )

        assert result == ResourcePreset(
            name="cpu-small", credits_per_hour=Decimal("10"), cpu=4.0, memory_mb=1024
        )

    def test_create_resource_preset_with_memory_gpu_tpu_preemptible_affinity(
        self, factory: EntityFactory
    ) -> None:
        result = factory.create_resource_preset(
            {
                "name": "gpu-small",
                "credits_per_hour": "10",
                "cpu": 4.0,
                "memory_mb": 12288,
                "gpu": 1,
                "gpu_model": "nvidia-tesla-k80",
                "tpu": {"type": "tpu", "software_version": "v1"},
                "scheduler_enabled": True,
                "preemptible_node": True,
                "resource_affinity": ["gpu-k80"],
            }
        )

        assert result == ResourcePreset(
            name="gpu-small",
            credits_per_hour=Decimal("10"),
            cpu=4.0,
            memory_mb=12288,
            gpu=1,
            gpu_model="nvidia-tesla-k80",
            tpu=TPUPreset(type="tpu", software_version="v1"),
            scheduler_enabled=True,
            preemptible_node=True,
            resource_affinity=["gpu-k80"],
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
                    {},
                    {"path": "/volume", "size_mb": 1024},
                ],
            }
        )

        assert result == StorageConfig(
            url=URL("https://storage-dev.neu.ro"),
            volumes=[
                VolumeConfig(),
                VolumeConfig(path="/volume", size_mb=1024),
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

    def test_create_metrics(self, factory: EntityFactory) -> None:
        result = factory.create_metrics({"url": "https://metrics-dev.neu.ro"})

        assert result == MetricsConfig(url=URL("https://metrics-dev.neu.ro"))

    def test_create_dns(self, factory: EntityFactory) -> None:
        result = factory.create_dns(
            {
                "name": "neu.ro",
                "a_records": [{"name": "*.jobs-dev.neu.ro.", "ips": ["192.168.0.2"]}],
            }
        )

        assert result == DNSConfig(name="neu.ro", a_records=[mock.ANY])

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
            {"url": "https://metrics-dev.neu.ro", "storage_limit_per_user_gb": 1024}
        )

        assert result == DisksConfig(
            url=URL("https://metrics-dev.neu.ro"), storage_limit_per_user_gb=1024
        )

    def test_create_buckets(self, factory: EntityFactory) -> None:
        result = factory.create_buckets(
            {"url": "https://buckets-dev.neu.ro", "disable_creation": True}
        )

        assert result == BucketsConfig(
            url=URL("https://buckets-dev.neu.ro"), disable_creation=True
        )

    def test_create_ingress(self, factory: EntityFactory) -> None:
        result = factory.create_ingress(
            {"acme_environment": "production", "cors_origins": ["https://app.neu.ro"]}
        )

        assert result == IngressConfig(
            acme_environment=ACMEEnvironment.PRODUCTION,
            cors_origins=["https://app.neu.ro"],
        )

    def test_create_ingress_defaults(self, factory: EntityFactory) -> None:
        result = factory.create_ingress({"acme_environment": "production"})

        assert result == IngressConfig(acme_environment=ACMEEnvironment.PRODUCTION)

    @pytest.fixture
    def google_cloud_provider_response(self) -> dict[str, Any]:
        return {
            "type": "gcp",
            "location_type": "zonal",
            "region": "us-central1",
            "zones": ["us-central1-a"],
            "project": "project",
            "credentials": {
                "type": "service_account",
                "project_id": "project_id",
                "private_key_id": "private_key_id",
                "private_key": "private_key",
                "client_email": "service.account@gmail.com",
                "client_id": "client_id",
                "auth_uri": "https://auth_uri",
                "token_uri": "https://token_uri",
                "auth_provider_x509_cert_url": "https://auth_provider_x509_cert_url",
                "client_x509_cert_url": "https://client_x509_cert_url",
            },
            "node_pools": [
                {
                    "id": "n1_highmem_8",
                    "name": "n1-highmem-8",
                    "role": "platform_job",
                    "machine_type": "n1-highmem-8",
                    "min_size": 0,
                    "max_size": 1,
                    "cpu": 8.0,
                    "available_cpu": 7.0,
                    "memory_mb": 52 * 1024,
                    "available_memory_mb": 45 * 1024,
                    "disk_size_gb": 700,
                },
                {
                    "id": "n1_highmem_32",
                    "name": "n1-highmem-32-1xk80-preemptible",
                    "role": "platform_job",
                    "machine_type": "n1-highmem-32",
                    "min_size": 0,
                    "max_size": 1,
                    "idle_size": 1,
                    "cpu": 32.0,
                    "available_cpu": 31.0,
                    "memory_mb": 208 * 1024,
                    "available_memory_mb": 201 * 1024,
                    "disk_size_gb": 700,
                    "gpu": 1,
                    "gpu_model": "nvidia-tesla-k80",
                    "is_preemptible": True,
                },
            ],
            "storage": {
                "id": "premium",
                "description": "GCP Filestore (Premium)",
                "backend": "filestore",
                "tier": "PREMIUM",
                "instances": [
                    {"size_mb": 5 * 1024 * 1024, "ready": False},
                    {"name": "org", "size_mb": 3 * 1024 * 1024, "ready": True},
                ],
            },
        }

    @pytest.fixture
    def google_cloud_provider(self) -> GoogleCloudProvider:
        return GoogleCloudProvider(
            location_type=ClusterLocationType.ZONAL,
            region="us-central1",
            zones=["us-central1-a"],
            project="project",
            credentials={
                "type": "service_account",
                "project_id": "project_id",
                "private_key_id": "private_key_id",
                "private_key": "private_key",
                "client_email": "service.account@gmail.com",
                "client_id": "client_id",
                "auth_uri": "https://auth_uri",
                "token_uri": "https://token_uri",
                "auth_provider_x509_cert_url": "https://auth_provider_x509_cert_url",
                "client_x509_cert_url": "https://client_x509_cert_url",
            },
            node_pools=[
                NodePool(
                    name="n1-highmem-8",
                    machine_type="n1-highmem-8",
                    min_size=0,
                    max_size=1,
                    cpu=8.0,
                    available_cpu=7.0,
                    memory_mb=52 * 1024,
                    available_memory_mb=45 * 1024,
                    disk_size_gb=700,
                ),
                NodePool(
                    name="n1-highmem-32-1xk80-preemptible",
                    machine_type="n1-highmem-32",
                    min_size=0,
                    max_size=1,
                    idle_size=1,
                    cpu=32.0,
                    available_cpu=31.0,
                    memory_mb=208 * 1024,
                    available_memory_mb=201 * 1024,
                    disk_size_gb=700,
                    gpu=1,
                    gpu_model="nvidia-tesla-k80",
                    is_preemptible=True,
                ),
            ],
            storage=GoogleStorage(
                id="premium",
                description="GCP Filestore (Premium)",
                tier=GoogleFilestoreTier.PREMIUM,
                instances=[
                    StorageInstance(size_mb=5 * 1024 * 1024),
                    StorageInstance(name="org", size_mb=3 * 1024 * 1024, ready=True),
                ],
            ),
        )

    def test_create_cloud_provider_google(
        self,
        factory: EntityFactory,
        google_cloud_provider: GoogleCloudProvider,
        google_cloud_provider_response: dict[str, Any],
    ) -> None:
        result = factory.create_cloud_provider(google_cloud_provider_response)
        assert result == google_cloud_provider

    @pytest.fixture
    def aws_cloud_provider_response(self) -> dict[str, Any]:
        return {
            "type": "aws",
            "region": "us-central-1",
            "zones": ["us-central-1a"],
            "vpc_id": "test-vpc",
            "credentials": {
                "access_key_id": "access_key_id",
                "secret_access_key": "secret_access_key",
            },
            "node_pools": [
                {
                    "id": "m5_2xlarge_8",
                    "role": "platform_job",
                    "name": "m5-2xlarge",
                    "machine_type": "m5.2xlarge",
                    "min_size": 0,
                    "max_size": 1,
                    "cpu": 8.0,
                    "available_cpu": 7.0,
                    "memory_mb": 32 * 1024,
                    "available_memory_mb": 28 * 1024,
                    "disk_size_gb": 700,
                },
                {
                    "id": "p2_xlarge_4",
                    "role": "platform_job",
                    "name": "p2-xlarge-1xk80-preemptible",
                    "machine_type": "p2.xlarge",
                    "min_size": 0,
                    "max_size": 1,
                    "idle_size": 1,
                    "cpu": 4.0,
                    "available_cpu": 3.0,
                    "memory_mb": 61 * 1024,
                    "available_memory_mb": 57 * 1024,
                    "disk_size_gb": 700,
                    "gpu": 1,
                    "gpu_model": "nvidia-tesla-k80",
                    "is_preemptible": True,
                },
            ],
            "storage": {
                "id": "generalpurpose_bursting",
                "description": "AWS EFS (generalPurpose, bursting)",
                "performance_mode": "generalPurpose",
                "throughput_mode": "bursting",
                "instances": [{"ready": False}, {"name": "org", "ready": True}],
            },
        }

    @pytest.fixture
    def aws_cloud_provider(self) -> AWSCloudProvider:
        return AWSCloudProvider(
            region="us-central-1",
            zones=["us-central-1a"],
            vpc_id="test-vpc",
            credentials=AWSCredentials(
                access_key_id="access_key_id", secret_access_key="secret_access_key"
            ),
            node_pools=[
                NodePool(
                    name="m5-2xlarge",
                    machine_type="m5.2xlarge",
                    min_size=0,
                    max_size=1,
                    cpu=8.0,
                    available_cpu=7.0,
                    memory_mb=32 * 1024,
                    available_memory_mb=28 * 1024,
                    disk_size_gb=700,
                ),
                NodePool(
                    name="p2-xlarge-1xk80-preemptible",
                    machine_type="p2.xlarge",
                    min_size=0,
                    max_size=1,
                    idle_size=1,
                    cpu=4.0,
                    available_cpu=3.0,
                    memory_mb=61 * 1024,
                    available_memory_mb=57 * 1024,
                    disk_size_gb=700,
                    gpu=1,
                    gpu_model="nvidia-tesla-k80",
                    is_preemptible=True,
                ),
            ],
            storage=AWSStorage(
                id="generalpurpose_bursting",
                description="AWS EFS (generalPurpose, bursting)",
                performance_mode=EFSPerformanceMode.GENERAL_PURPOSE,
                throughput_mode=EFSThroughputMode.BURSTING,
                instances=[StorageInstance(), StorageInstance(name="org", ready=True)],
            ),
        )

    def test_create_cloud_provider_aws(
        self,
        factory: EntityFactory,
        aws_cloud_provider: AWSCloudProvider,
        aws_cloud_provider_response: dict[str, Any],
    ) -> None:
        result = factory.create_cloud_provider(aws_cloud_provider_response)
        assert result == aws_cloud_provider

    @pytest.fixture
    def azure_cloud_provider_response(self) -> dict[str, Any]:
        return {
            "type": "azure",
            "region": "westus",
            "resource_group": "resource_group",
            "credentials": {
                "subscription_id": "subscription_id",
                "tenant_id": "tenant_id",
                "client_id": "client_id",
                "client_secret": "client_secret",
            },
            "node_pools": [
                {
                    "id": "standard_d8s_v3_8",
                    "role": "platform_job",
                    "name": "Standard_D8s_v3",
                    "machine_type": "Standard_D8s_v3",
                    "min_size": 0,
                    "max_size": 1,
                    "cpu": 8.0,
                    "available_cpu": 7.0,
                    "memory_mb": 32 * 1024,
                    "available_memory_mb": 28 * 1024,
                    "disk_size_gb": 700,
                },
                {
                    "id": "standard_nc6_6",
                    "role": "platform_job",
                    "name": "Standard_NC6-1xk80-preemptible",
                    "machine_type": "Standard_NC6",
                    "min_size": 0,
                    "max_size": 1,
                    "idle_size": 1,
                    "cpu": 6.0,
                    "available_cpu": 5.0,
                    "memory_mb": 56 * 1024,
                    "available_memory_mb": 50 * 1024,
                    "disk_size_gb": 700,
                    "gpu": 1,
                    "gpu_model": "nvidia-tesla-k80",
                    "is_preemptible": True,
                },
            ],
            "storage": {
                "id": "premium_lrs",
                "description": "Azure Files (Premium, LRS replication)",
                "tier": "Premium",
                "replication_type": "LRS",
                "instances": [
                    {"size_mb": 100 * 1024, "ready": False},
                    {"name": "org", "size_mb": 200 * 1024, "ready": True},
                ],
            },
        }

    @pytest.fixture
    def azure_cloud_provider(self) -> AzureCloudProvider:
        return AzureCloudProvider(
            region="westus",
            resource_group="resource_group",
            credentials=AzureCredentials(
                subscription_id="subscription_id",
                tenant_id="tenant_id",
                client_id="client_id",
                client_secret="client_secret",
            ),
            node_pools=[
                NodePool(
                    name="Standard_D8s_v3",
                    machine_type="Standard_D8s_v3",
                    min_size=0,
                    max_size=1,
                    cpu=8.0,
                    available_cpu=7.0,
                    memory_mb=32 * 1024,
                    available_memory_mb=28 * 1024,
                    disk_size_gb=700,
                ),
                NodePool(
                    name="Standard_NC6-1xk80-preemptible",
                    machine_type="Standard_NC6",
                    min_size=0,
                    max_size=1,
                    idle_size=1,
                    cpu=6.0,
                    available_cpu=5.0,
                    memory_mb=56 * 1024,
                    available_memory_mb=50 * 1024,
                    disk_size_gb=700,
                    gpu=1,
                    gpu_model="nvidia-tesla-k80",
                    is_preemptible=True,
                ),
            ],
            storage=AzureStorage(
                id="premium_lrs",
                description="Azure Files (Premium, LRS replication)",
                tier=AzureStorageTier.PREMIUM,
                replication_type=AzureReplicationType.LRS,
                instances=[
                    StorageInstance(size_mb=100 * 1024),
                    StorageInstance(name="org", size_mb=200 * 1024, ready=True),
                ],
            ),
        )

    def test_create_cloud_provider_azure(
        self,
        factory: EntityFactory,
        azure_cloud_provider: AzureCloudProvider,
        azure_cloud_provider_response: dict[str, Any],
    ) -> None:
        result = factory.create_cloud_provider(azure_cloud_provider_response)
        assert result == azure_cloud_provider

    @pytest.fixture
    def on_prem_cloud_provider_response(self) -> dict[str, Any]:
        return {
            "type": "on_prem",
            "kubernetes_url": "localhost:8001",
            "credentials": {
                "token": "kubernetes-token",
                "ca_data": "kubernetes-ca-data",
            },
            "node_pools": [
                {
                    "role": "platform_job",
                    "min_size": 1,
                    "max_size": 1,
                    "name": "cpu-machine",
                    "machine_type": "cpu-machine",
                    "cpu": 1.0,
                    "available_cpu": 1.0,
                    "memory_mb": 1024,
                    "available_memory_mb": 1024,
                    "disk_size_gb": 700,
                },
                {
                    "role": "platform_job",
                    "min_size": 1,
                    "max_size": 1,
                    "name": "gpu-machine-1xk80",
                    "machine_type": "gpu-machine-1xk80",
                    "cpu": 1.0,
                    "available_cpu": 1.0,
                    "memory_mb": 1024,
                    "available_memory_mb": 1024,
                    "disk_size_gb": 700,
                    "gpu": 1,
                    "gpu_model": "nvidia-tesla-k80",
                    "price": "0.9",
                    "currency": "USD",
                },
            ],
        }

    @pytest.fixture
    def on_prem_cloud_provider(self) -> OnPremCloudProvider:
        return OnPremCloudProvider(
            kubernetes_url=URL("localhost:8001"),
            credentials=KubernetesCredentials(
                token="kubernetes-token", ca_data="kubernetes-ca-data"
            ),
            node_pools=[
                NodePool(
                    min_size=1,
                    max_size=1,
                    name="cpu-machine",
                    cpu=1.0,
                    available_cpu=1.0,
                    memory_mb=1024,
                    available_memory_mb=1024,
                    disk_size_gb=700,
                    machine_type="cpu-machine",
                ),
                NodePool(
                    min_size=1,
                    max_size=1,
                    name="gpu-machine-1xk80",
                    cpu=1.0,
                    available_cpu=1.0,
                    memory_mb=1024,
                    available_memory_mb=1024,
                    disk_size_gb=700,
                    gpu=1,
                    gpu_model="nvidia-tesla-k80",
                    price=Decimal("0.9"),
                    currency="USD",
                    machine_type="gpu-machine-1xk80",
                ),
            ],
            storage=None,
        )

    def test_create_cloud_provider_on_prem(
        self,
        factory: EntityFactory,
        on_prem_cloud_provider: OnPremCloudProvider,
        on_prem_cloud_provider_response: dict[str, Any],
    ) -> None:
        result = factory.create_cloud_provider(on_prem_cloud_provider_response)
        assert result == on_prem_cloud_provider

    @pytest.fixture
    def vcd_cloud_provider_response(self) -> dict[str, Any]:
        return {
            "type": "vcd_mts",
            "url": "vcd_url",
            "organization": "vcd_org",
            "virtual_data_center": "vdc",
            "edge_name": "edge",
            "edge_external_network_name": "edge-external-network",
            "edge_public_ip": "10.0.0.1",
            "catalog_name": "catalog",
            "credentials": {
                "user": "vcd_user",
                "password": "vcd_password",
                "ssh_password": "ssh-password",
            },
            "node_pools": [
                {
                    "id": "master_neuro_8",
                    "role": "platform_job",
                    "min_size": 1,
                    "max_size": 1,
                    "name": "Master-neuro",
                    "machine_type": "Master-neuro",
                    "cpu": 8.0,
                    "available_cpu": 7.0,
                    "memory_mb": 32 * 1024,
                    "available_memory_mb": 29 * 1024,
                    "disk_size_gb": 700,
                },
                {
                    "id": "x16_neuro_16",
                    "role": "platform_job",
                    "min_size": 1,
                    "max_size": 1,
                    "name": "X16-neuro-1xk80",
                    "machine_type": "X16-neuro",
                    "cpu": 16.0,
                    "available_cpu": 15.0,
                    "memory_mb": 40 * 1024,
                    "available_memory_mb": 37 * 1024,
                    "disk_size_gb": 700,
                    "gpu": 1,
                    "gpu_model": "nvidia-tesla-k80",
                    "price": "0.9",
                    "currency": "USD",
                },
            ],
            "storage": {
                "profile_name": "profile",
                "size_gib": 10,
                "instances": [
                    {"size_mb": 7 * 1024, "ready": False},
                    {"name": "org", "size_mb": 3 * 1024, "ready": True},
                ],
                "description": "profile",
            },
        }

    @pytest.fixture
    def vcd_cloud_provider(self) -> VCDCloudProvider:
        return VCDCloudProvider(
            _type=CloudProviderType.VCD_MTS,
            url=URL("vcd_url"),
            organization="vcd_org",
            virtual_data_center="vdc",
            edge_name="edge",
            edge_external_network_name="edge-external-network",
            edge_public_ip="10.0.0.1",
            catalog_name="catalog",
            credentials=VCDCredentials(
                user="vcd_user", password="vcd_password", ssh_password="ssh-password"
            ),
            node_pools=[
                NodePool(
                    min_size=1,
                    max_size=1,
                    name="Master-neuro",
                    machine_type="Master-neuro",
                    cpu=8.0,
                    available_cpu=7.0,
                    memory_mb=32 * 1024,
                    available_memory_mb=29 * 1024,
                    disk_size_gb=700,
                ),
                NodePool(
                    min_size=1,
                    max_size=1,
                    name="X16-neuro-1xk80",
                    machine_type="X16-neuro",
                    cpu=16.0,
                    available_cpu=15.0,
                    memory_mb=40 * 1024,
                    available_memory_mb=37 * 1024,
                    disk_size_gb=700,
                    gpu=1,
                    gpu_model="nvidia-tesla-k80",
                    price=Decimal("0.9"),
                    currency="USD",
                ),
            ],
            storage=VCDStorage(
                description="profile",
                profile_name="profile",
                size_gib=10,
                instances=[
                    StorageInstance(size_mb=7 * 1024),
                    StorageInstance(name="org", size_mb=3 * 1024, ready=True),
                ],
            ),
        )

    def test_create_cloud_provider_vcd(
        self,
        factory: EntityFactory,
        vcd_cloud_provider: VCDCloudProvider,
        vcd_cloud_provider_response: dict[str, Any],
    ) -> None:
        result = factory.create_cloud_provider(vcd_cloud_provider_response)
        assert result == vcd_cloud_provider

    @pytest.fixture
    def credentials(self) -> dict[str, Any]:
        return {
            "neuro": {
                "url": "https://neu.ro",
                "token": "cluster_token",
            },
            "neuro_registry": {
                "url": "https://ghcr.io/neuro-inc",
                "username": "username",
                "password": "password",
                "email": "username@neu.ro",
            },
            "neuro_helm": {
                "url": "oci://neuro-inc.ghcr.io",
                "username": "username",
                "password": "password",
            },
            "grafana": {
                "username": "username",
                "password": "password",
            },
            "sentry": {
                "client_key_id": "key",
                "public_dsn": "dsn",
                "sample_rate": 0.2,
            },
            "docker_hub": {
                "url": "https://index.docker.io/v1",
                "username": "test",
                "password": "password",
                "email": "test@neu.ro",
            },
            "minio": {
                "username": "test",
                "password": "password",
            },
            "emc_ecs": {
                "access_key_id": "key_id",
                "secret_access_key": "secret_key",
                "s3_endpoint": "https://emc-ecs.s3",
                "management_endpoint": "https://emc-ecs.management",
                "s3_assumable_role": "s3-role",
            },
            "open_stack": {
                "account_id": "id",
                "password": "password",
                "s3_endpoint": "https://os.s3",
                "endpoint": "https://os.management",
                "region_name": "region",
            },
        }

    def test_create_credentials(
        self, factory: EntityFactory, credentials: dict[str, Any]
    ) -> None:
        result = factory.create_credentials(credentials)

        assert result == CredentialsConfig(
            neuro=NeuroAuthConfig(
                url=URL("https://neu.ro"),
                token="cluster_token",
            ),
            neuro_registry=DockerRegistryConfig(
                url=URL("https://ghcr.io/neuro-inc"),
                username="username",
                password="password",
                email="username@neu.ro",
            ),
            neuro_helm=HelmRegistryConfig(
                url=URL("oci://neuro-inc.ghcr.io"),
                username="username",
                password="password",
            ),
            grafana=GrafanaCredentials(
                username="username",
                password="password",
            ),
            sentry=SentryCredentials(
                client_key_id="key", public_dsn=URL("dsn"), sample_rate=0.2
            ),
            docker_hub=DockerRegistryConfig(
                url=URL("https://index.docker.io/v1"),
                username="test",
                password="password",
                email="test@neu.ro",
            ),
            minio=MinioCredentials(
                username="test",
                password="password",
            ),
            emc_ecs=EMCECSCredentials(
                access_key_id="key_id",
                secret_access_key="secret_key",
                s3_endpoint=URL("https://emc-ecs.s3"),
                management_endpoint=URL("https://emc-ecs.management"),
                s3_assumable_role="s3-role",
            ),
            open_stack=OpenStackCredentials(
                account_id="id",
                password="password",
                s3_endpoint=URL("https://os.s3"),
                endpoint=URL("https://os.management"),
                region_name="region",
            ),
        )

    def test_create_minimal_credentials(
        self, factory: EntityFactory, credentials: dict[str, Any]
    ) -> None:
        del credentials["grafana"]
        del credentials["sentry"]
        del credentials["docker_hub"]
        del credentials["minio"]
        del credentials["emc_ecs"]
        del credentials["open_stack"]
        result = factory.create_credentials(credentials)

        assert result == CredentialsConfig(
            neuro=NeuroAuthConfig(
                url=URL("https://neu.ro"),
                token="cluster_token",
            ),
            neuro_registry=DockerRegistryConfig(
                url=URL("https://ghcr.io/neuro-inc"),
                username="username",
                password="password",
                email="username@neu.ro",
            ),
            neuro_helm=HelmRegistryConfig(
                url=URL("oci://neuro-inc.ghcr.io"),
                username="username",
                password="password",
            ),
        )


class TestPayloadFactory:
    @pytest.fixture
    def factory(self) -> PayloadFactory:
        return PayloadFactory()

    def test_create_orchestrator(self, factory: PayloadFactory) -> None:
        result = factory.create_orchestrator(
            OrchestratorConfig(
                job_hostname_template="{job_id}.jobs-dev.neu.ro",
                job_internal_hostname_template="{job_id}.platform-jobs",
                job_fallback_hostname="default.jobs-dev.neu.ro",
                job_schedule_timeout_s=1,
                job_schedule_scale_up_timeout_s=2,
                is_http_ingress_secure=False,
                resource_pool_types=[ResourcePoolType(name="cpu")],
                resource_presets=[
                    ResourcePreset(
                        name="cpu-micro",
                        credits_per_hour=Decimal(10),
                        cpu=0.1,
                        memory_mb=100,
                    )
                ],
                allow_privileged_mode=False,
                pre_pull_images=["neuromation/base"],
                idle_jobs=[
                    IdleJobConfig(
                        name="idle",
                        count=1,
                        image="miner",
                        resources=Resources(cpu_m=1000, memory_mb=1024),
                    )
                ],
            )
        )

        assert result == {
            "job_hostname_template": "{job_id}.jobs-dev.neu.ro",
            "job_internal_hostname_template": "{job_id}.platform-jobs",
            "job_fallback_hostname": "default.jobs-dev.neu.ro",
            "job_schedule_timeout_s": 1,
            "job_schedule_scale_up_timeout_s": 2,
            "is_http_ingress_secure": False,
            "resource_pool_types": [mock.ANY],
            "resource_presets": [mock.ANY],
            "allow_privileged_mode": False,
            "pre_pull_images": ["neuromation/base"],
            "idle_jobs": [
                {
                    "name": "idle",
                    "count": 1,
                    "image": "miner",
                    "resources": {"cpu_m": 1000, "memory_mb": 1024},
                }
            ],
        }

    def test_create_orchestrator_default(self, factory: PayloadFactory) -> None:
        result = factory.create_orchestrator(
            OrchestratorConfig(
                job_hostname_template="{job_id}.jobs-dev.neu.ro",
                job_internal_hostname_template="",
                job_fallback_hostname="default.jobs-dev.neu.ro",
                job_schedule_timeout_s=1,
                job_schedule_scale_up_timeout_s=2,
                is_http_ingress_secure=False,
                allow_privileged_mode=False,
            )
        )

        assert result == {
            "job_hostname_template": "{job_id}.jobs-dev.neu.ro",
            "job_fallback_hostname": "default.jobs-dev.neu.ro",
            "job_schedule_timeout_s": 1,
            "job_schedule_scale_up_timeout_s": 2,
            "is_http_ingress_secure": False,
            "allow_privileged_mode": False,
        }

    def test_create_resource_pool_type(self, factory: PayloadFactory) -> None:
        result = factory.create_resource_pool_type(
            ResourcePoolType(
                name="n1-highmem-4",
                min_size=1,
                max_size=2,
                idle_size=1,
                cpu=4.0,
                available_cpu=3.0,
                memory_mb=12 * 1024,
                available_memory_mb=10 * 1024,
                disk_size_gb=700,
                gpu=1,
                gpu_model="nvidia-tesla-k80",
                tpu=TPUResource(
                    ipv4_cidr_block="10.0.0.0/8",
                    types=["tpu"],
                    software_versions=["v1"],
                ),
                is_preemptible=True,
                price=Decimal("1.0"),
                currency="USD",
            )
        )

        assert result == {
            "name": "n1-highmem-4",
            "min_size": 1,
            "max_size": 2,
            "idle_size": 1,
            "cpu": 4.0,
            "available_cpu": 3.0,
            "memory_mb": 12 * 1024,
            "available_memory_mb": 10 * 1024,
            "disk_size_gb": 700,
            "gpu": 1,
            "gpu_model": "nvidia-tesla-k80",
            "tpu": {
                "ipv4_cidr_block": "10.0.0.0/8",
                "types": ["tpu"],
                "software_versions": ["v1"],
            },
            "is_preemptible": True,
            "price": "1.0",
            "currency": "USD",
        }

    def test_create_empty_resource_pool_type(self, factory: PayloadFactory) -> None:
        result = factory.create_resource_pool_type(ResourcePoolType(name="node-pool"))

        assert result == {
            "name": "node-pool",
            "available_cpu": 1.0,
            "available_memory_mb": 1024,
            "cpu": 1.0,
            "disk_size_gb": 150,
            "idle_size": 0,
            "is_preemptible": False,
            "max_size": 1,
            "memory_mb": 1024,
            "min_size": 0,
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
                memory_mb=1024,
            )
        )

        assert result == {
            "name": "cpu-small",
            "credits_per_hour": "10",
            "cpu": 4.0,
            "memory_mb": 1024,
        }

    def test_create_resource_preset_with_memory_gpu_tpu_preemptible_affinity(
        self, factory: PayloadFactory
    ) -> None:
        result = factory.create_resource_preset(
            ResourcePreset(
                name="gpu-small",
                credits_per_hour=Decimal("10"),
                cpu=4.0,
                memory_mb=12288,
                gpu=1,
                gpu_model="nvidia-tesla-k80",
                tpu=TPUPreset(type="tpu", software_version="v1"),
                scheduler_enabled=True,
                preemptible_node=True,
                resource_affinity=["gpu-k80"],
            )
        )

        assert result == {
            "name": "gpu-small",
            "credits_per_hour": "10",
            "cpu": 4.0,
            "memory_mb": 12288,
            "gpu": 1,
            "gpu_model": "nvidia-tesla-k80",
            "tpu": {"type": "tpu", "software_version": "v1"},
            "scheduler_enabled": True,
            "preemptible_node": True,
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
                    VolumeConfig(),
                    VolumeConfig(path="/volume", size_mb=1024),
                ],
            )
        )

        assert result == {
            "url": "https://storage-dev.neu.ro",
            "volumes": [
                {},
                {"path": "/volume", "size_mb": 1024},
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

    def test_create_metrics(self, factory: PayloadFactory) -> None:
        result = factory.create_metrics(
            MetricsConfig(url=URL("https://metrics-dev.neu.ro"))
        )

        assert result == {"url": "https://metrics-dev.neu.ro"}

    def test_create_dns(self, factory: PayloadFactory) -> None:
        result = factory.create_dns(
            DNSConfig(
                name="neu.ro",
                a_records=[ARecord(name="*.jobs-dev.neu.ro.", ips=["192.168.0.2"])],
            )
        )

        assert result == {
            "name": "neu.ro",
            "a_records": [{"name": "*.jobs-dev.neu.ro.", "ips": ["192.168.0.2"]}],
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
                url=URL("https://metrics-dev.neu.ro"), storage_limit_per_user_gb=1024
            )
        )

        assert result == {
            "url": "https://metrics-dev.neu.ro",
            "storage_limit_per_user_gb": 1024,
        }

    def test_create_buckets(self, factory: PayloadFactory) -> None:
        result = factory.create_buckets(
            BucketsConfig(url=URL("https://buckets-dev.neu.ro"), disable_creation=True)
        )

        assert result == {"url": "https://buckets-dev.neu.ro", "disable_creation": True}

    def test_create_ingress(self, factory: PayloadFactory) -> None:
        result = factory.create_ingress(
            IngressConfig(
                acme_environment=ACMEEnvironment.PRODUCTION,
                cors_origins=["https://app.neu.ro"],
            )
        )

        assert result == {
            "acme_environment": "production",
            "cors_origins": ["https://app.neu.ro"],
        }

    def test_create_ingress_defaults(self, factory: PayloadFactory) -> None:
        result = factory.create_ingress(
            IngressConfig(acme_environment=ACMEEnvironment.PRODUCTION)
        )

        assert result == {"acme_environment": "production"}

    @pytest.fixture
    def credentials(self) -> CredentialsConfig:
        return CredentialsConfig(
            neuro=NeuroAuthConfig(
                url=URL("https://neu.ro"),
                token="cluster_token",
            ),
            neuro_registry=DockerRegistryConfig(
                url=URL("https://ghcr.io/neuro-inc"),
                username="username",
                password="password",
                email="username@neu.ro",
            ),
            neuro_helm=HelmRegistryConfig(
                url=URL("oci://neuro-inc.ghcr.io"),
                username="username",
                password="password",
            ),
            grafana=GrafanaCredentials(
                username="username",
                password="password",
            ),
            sentry=SentryCredentials(
                client_key_id="key", public_dsn=URL("dsn"), sample_rate=0.2
            ),
            docker_hub=DockerRegistryConfig(
                url=URL("https://index.docker.io/v1"),
                username="test",
                password="password",
                email="test@neu.ro",
            ),
            minio=MinioCredentials(
                username="test",
                password="password",
            ),
            emc_ecs=EMCECSCredentials(
                access_key_id="key_id",
                secret_access_key="secret_key",
                s3_endpoint=URL("https://emc-ecs.s3"),
                management_endpoint=URL("https://emc-ecs.management"),
                s3_assumable_role="s3-role",
            ),
            open_stack=OpenStackCredentials(
                account_id="id",
                password="password",
                s3_endpoint=URL("https://os.s3"),
                endpoint=URL("https://os.management"),
                region_name="region",
            ),
        )

    def test_create_credentials(
        self, factory: PayloadFactory, credentials: CredentialsConfig
    ) -> None:
        result = factory.create_credentials(credentials)

        assert result == {
            "neuro": {"token": "cluster_token"},
            "neuro_registry": {"username": "username", "password": "password"},
            "neuro_helm": {"username": "username", "password": "password"},
            "grafana": {
                "username": "username",
                "password": "password",
            },
            "sentry": {
                "client_key_id": "key",
                "public_dsn": "dsn",
                "sample_rate": 0.2,
            },
            "docker_hub": {"username": "test", "password": "password"},
            "minio": {
                "username": "test",
                "password": "password",
            },
            "emc_ecs": {
                "access_key_id": "key_id",
                "secret_access_key": "secret_key",
                "s3_endpoint": "https://emc-ecs.s3",
                "management_endpoint": "https://emc-ecs.management",
                "s3_assumable_role": "s3-role",
            },
            "open_stack": {
                "account_id": "id",
                "password": "password",
                "s3_endpoint": "https://os.s3",
                "endpoint": "https://os.management",
                "region_name": "region",
            },
        }

    def test_create_minimal_credentials(
        self, factory: PayloadFactory, credentials: CredentialsConfig
    ) -> None:
        credentials = replace(
            credentials,
            grafana=None,
            sentry=None,
            docker_hub=None,
            minio=None,
            emc_ecs=None,
            open_stack=None,
        )
        result = factory.create_credentials(credentials)

        assert result == {
            "neuro": {"token": "cluster_token"},
            "neuro_registry": {"username": "username", "password": "password"},
            "neuro_helm": {"username": "username", "password": "password"},
        }
