from decimal import Decimal
from typing import Any
from unittest import mock

import pytest
from yarl import URL

from neuro_config_client.converters import PrimitiveToClusterConverter
from neuro_config_client.models import (
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
    BlobStorageConfig,
    BucketsConfig,
    CloudProviderType,
    Cluster,
    ClusterLocationType,
    DisksConfig,
    DNSConfig,
    EFSPerformanceMode,
    EFSThroughputMode,
    GoogleCloudProvider,
    GoogleFilestoreTier,
    GoogleStorage,
    GoogleStorageBackend,
    IdleJobConfig,
    IngressConfig,
    KubernetesCredentials,
    MetricsConfig,
    MonitoringConfig,
    NodePool,
    OnPremCloudProvider,
    OrchestratorConfig,
    RegistryConfig,
    ResourcePoolType,
    ResourcePreset,
    Resources,
    SecretsConfig,
    StorageConfig,
    StorageInstance,
    TPUPreset,
    TPUResource,
    VCDCloudProvider,
    VCDCredentials,
    VCDStorage,
    VolumeConfig,
)


class TestPrimitiveToCLusterConverter:
    @pytest.fixture
    def converter(self) -> PrimitiveToClusterConverter:
        return PrimitiveToClusterConverter()

    def test_convert_empty_cluster(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_cluster({"name": "default"})

        assert result == Cluster(name="default")

    def test_convert_cluster(
        self,
        converter: PrimitiveToClusterConverter,
        google_cloud_provider_response: dict[str, Any],
    ) -> None:
        result = converter.convert_cluster(
            {
                "name": "default",
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
            }
        )

        assert result.name == "default"
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

    def test_convert_orchestrator(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_orchestrator(
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
                    count=1,
                    image="miner",
                    resources=Resources(cpu_m=1000, memory_mb=1024),
                )
            ],
        )

    def test_convert_orchestrator_default(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_orchestrator(
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
            job_internal_hostname_template="",
            job_fallback_hostname="default.jobs-dev.neu.ro",
            job_schedule_timeout_s=1,
            job_schedule_scale_up_timeout_s=2,
            is_http_ingress_secure=False,
            allow_privileged_mode=False,
        )

    def test_convert_resource_pool_type(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_resource_pool_type(
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

    def test_convert_empty_resource_pool_type(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_resource_pool_type({"name": "node-pool"})

        assert result == ResourcePoolType(name="node-pool")

    def test_convert_tpu_resource(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_tpu_resource(
            {
                "ipv4_cidr_block": "10.0.0.0/8",
                "types": ["tpu"],
                "software_versions": ["v1"],
            }
        )

        assert result == TPUResource(
            ipv4_cidr_block="10.0.0.0/8", types=["tpu"], software_versions=["v1"]
        )

    def test_convert_resource_preset(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_resource_preset(
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

    def test_convert_resource_preset_with_memory_gpu_tpu_preemptible_affinity(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_resource_preset(
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

    def test_convert_storage(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_storage({"url": "https://storage-dev.neu.ro"})

        assert result == StorageConfig(
            url=URL("https://storage-dev.neu.ro"), volumes=[]
        )

    def test_convert_storage_with_volumes(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_storage(
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

    def test_convert_blob_storage(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_blob_storage(
            {"url": "https://blob-storage-dev.neu.ro"}
        )

        assert result == BlobStorageConfig(url=URL("https://blob-storage-dev.neu.ro"))

    def test_convert_registry(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_registry({"url": "https://registry-dev.neu.ro"})

        assert result == RegistryConfig(url=URL("https://registry-dev.neu.ro"))

    def test_convert_monitoring(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_monitoring({"url": "https://monitoring-dev.neu.ro"})

        assert result == MonitoringConfig(url=URL("https://monitoring-dev.neu.ro"))

    def test_convert_secrets(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_secrets({"url": "https://secrets-dev.neu.ro"})

        assert result == SecretsConfig(url=URL("https://secrets-dev.neu.ro"))

    def test_convert_metrics(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_metrics({"url": "https://metrics-dev.neu.ro"})

        assert result == MetricsConfig(url=URL("https://metrics-dev.neu.ro"))

    def test_convert_dns(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_dns(
            {
                "name": "neu.ro",
                "a_records": [{"name": "*.jobs-dev.neu.ro.", "ips": ["192.168.0.2"]}],
            }
        )

        assert result == DNSConfig(name="neu.ro", a_records=[mock.ANY])

    def test_convert_a_record_with_ips(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_a_record(
            {"name": "*.jobs-dev.neu.ro.", "ips": ["192.168.0.2"]}
        )

        assert result == ARecord(name="*.jobs-dev.neu.ro.", ips=["192.168.0.2"])

    def test_convert_a_record_dns_name(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_a_record(
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

    def test_convert_disks(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_disks(
            {"url": "https://metrics-dev.neu.ro", "storage_limit_per_user_gb": 1024}
        )

        assert result == DisksConfig(
            url=URL("https://metrics-dev.neu.ro"), storage_limit_per_user_gb=1024
        )

    def test_convert_buckets(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_buckets(
            {"url": "https://buckets-dev.neu.ro", "disable_creation": True}
        )

        assert result == BucketsConfig(
            url=URL("https://buckets-dev.neu.ro"), disable_creation=True
        )

    def test_convert_ingress(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_ingress(
            {"acme_environment": "production", "cors_origins": ["https://app.neu.ro"]}
        )

        assert result == IngressConfig(
            acme_environment=ACMEEnvironment.PRODUCTION,
            cors_origins=["https://app.neu.ro"],
        )

    def test_convert_ingress_defaults(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_ingress({"acme_environment": "production"})

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
                backend=GoogleStorageBackend.FILESTORE,
                tier=GoogleFilestoreTier.PREMIUM,
                instances=[
                    StorageInstance(size_mb=5 * 1024 * 1024),
                    StorageInstance(name="org", size_mb=3 * 1024 * 1024, ready=True),
                ],
            ),
        )

    def test_convert_cloud_provider_google(
        self,
        converter: PrimitiveToClusterConverter,
        google_cloud_provider: GoogleCloudProvider,
        google_cloud_provider_response: dict[str, Any],
    ) -> None:
        result = converter.convert_cloud_provider(google_cloud_provider_response)
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

    def test_convert_cloud_provider_aws(
        self,
        converter: PrimitiveToClusterConverter,
        aws_cloud_provider: AWSCloudProvider,
        aws_cloud_provider_response: dict[str, Any],
    ) -> None:
        result = converter.convert_cloud_provider(aws_cloud_provider_response)
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

    def test_convert_cloud_provider_azure(
        self,
        converter: PrimitiveToClusterConverter,
        azure_cloud_provider: AzureCloudProvider,
        azure_cloud_provider_response: dict[str, Any],
    ) -> None:
        result = converter.convert_cloud_provider(azure_cloud_provider_response)
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

    def test_convert_cloud_provider_on_prem(
        self,
        converter: PrimitiveToClusterConverter,
        on_prem_cloud_provider: OnPremCloudProvider,
        on_prem_cloud_provider_response: dict[str, Any],
    ) -> None:
        result = converter.convert_cloud_provider(on_prem_cloud_provider_response)
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

    def test_convert_cloud_provider_vcd(
        self,
        converter: PrimitiveToClusterConverter,
        vcd_cloud_provider: VCDCloudProvider,
        vcd_cloud_provider_response: dict[str, Any],
    ) -> None:
        result = converter.convert_cloud_provider(vcd_cloud_provider_response)
        assert result == vcd_cloud_provider
