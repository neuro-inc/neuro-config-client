from __future__ import annotations

import abc
import enum
from collections.abc import Sequence
from dataclasses import dataclass, field
from decimal import Decimal

from yarl import URL


class CloudProviderType(str, enum.Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ON_PREM = "on_prem"
    VCD_MTS = "vcd_mts"
    VCD_SELECTEL = "vcd_selectel"


class NodeRole(str, enum.Enum):
    KUBERNETES = "kubernetes"
    PLATFORM = "platform"
    PLATFORM_JOB = "platform_job"


@dataclass(frozen=True)
class NodePool:
    name: str
    role: NodeRole = NodeRole.PLATFORM_JOB

    min_size: int = 0
    max_size: int = 1
    idle_size: int = 0

    machine_type: str | None = None
    cpu: float = 1
    available_cpu: float = 1
    memory_mb: int = 1024
    available_memory_mb: int = 1024

    disk_size_gb: int = 20
    disk_type: str | None = None

    gpu: int | None = None
    gpu_model: str | None = None

    price: Decimal = Decimal()
    currency: str | None = None

    is_preemptible: bool = False

    zones: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class StorageInstance:
    size_mb: int | None = None
    name: str | None = None
    ready: bool = False


@dataclass(frozen=True)
class Storage:
    instances: list[StorageInstance]


# about 'type ignore': see https://github.com/python/mypy/issues/5374
@dataclass(frozen=True)  # type: ignore
class CloudProvider(abc.ABC):
    node_pools: Sequence[NodePool]
    storage: Storage | None

    @property
    @abc.abstractmethod
    def type(self) -> CloudProviderType:
        pass


@dataclass(frozen=True, repr=False)
class AWSCredentials:
    access_key_id: str
    secret_access_key: str


class EFSPerformanceMode(str, enum.Enum):
    GENERAL_PURPOSE = "generalPurpose"
    MAX_IO = "maxIO"


class EFSThroughputMode(str, enum.Enum):
    BURSTING = "bursting"
    PROVISIONED = "provisioned"


@dataclass(frozen=True)
class AWSStorage(Storage):
    id: str
    description: str
    performance_mode: EFSPerformanceMode
    throughput_mode: EFSThroughputMode


@dataclass(frozen=True)
class AWSCloudProvider(CloudProvider):
    region: str
    zones: Sequence[str]
    credentials: AWSCredentials = field(repr=False)
    storage: AWSStorage | None
    vpc_id: str | None = None

    @property
    def type(self) -> CloudProviderType:
        return CloudProviderType.AWS


class ClusterLocationType(str, enum.Enum):
    ZONAL = "zonal"
    REGIONAL = "regional"


class GoogleStorageBackend(str, enum.Enum):
    FILESTORE = "filestore"  # Google Cloud Filestore
    GCS_NFS = "gcs-nfs"  # Google Cloud Storage


class GoogleFilestoreTier(str, enum.Enum):
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"


@dataclass(frozen=True)
class GoogleStorage(Storage):
    id: str
    description: str
    backend: GoogleStorageBackend
    tier: GoogleFilestoreTier | None = None


@dataclass(frozen=True)
class GoogleCloudProvider(CloudProvider):
    region: str
    zones: Sequence[str]
    project: str
    credentials: dict[str, str] = field(repr=False)
    location_type: ClusterLocationType = ClusterLocationType.ZONAL
    tpu_enabled: bool = False

    @property
    def type(self) -> CloudProviderType:
        return CloudProviderType.GCP


@dataclass(frozen=True)
class AzureCredentials:
    subscription_id: str
    tenant_id: str
    client_id: str
    client_secret: str


class AzureStorageTier(str, enum.Enum):
    STANDARD = "Standard"
    PREMIUM = "Premium"


class AzureReplicationType(str, enum.Enum):
    LRS = "LRS"
    ZRS = "ZRS"


@dataclass(frozen=True)
class AzureStorage(Storage):
    id: str
    description: str
    tier: AzureStorageTier
    replication_type: AzureReplicationType


@dataclass(frozen=True)
class AzureCloudProvider(CloudProvider):
    region: str
    resource_group: str
    credentials: AzureCredentials
    virtual_network_cidr: str = ""

    @property
    def type(self) -> CloudProviderType:
        return CloudProviderType.AZURE


@dataclass(frozen=True)
class KubernetesCredentials:
    ca_data: str
    token: str = ""
    client_key_data: str = ""
    client_cert_data: str = ""


@dataclass(frozen=True)
class OnPremCloudProvider(CloudProvider):
    kubernetes_url: URL | None = None
    credentials: KubernetesCredentials | None = None

    @property
    def type(self) -> CloudProviderType:
        return CloudProviderType.ON_PREM


@dataclass(frozen=True)
class VCDCredentials:
    user: str
    password: str
    ssh_password: str


@dataclass(frozen=True)
class VCDStorage(Storage):
    description: str
    profile_name: str
    size_gib: int


@dataclass(frozen=True)
class VCDCloudProvider(CloudProvider):
    _type: CloudProviderType
    url: URL
    organization: str
    virtual_data_center: str
    edge_name: str
    edge_public_ip: str
    edge_external_network_name: str
    catalog_name: str
    credentials: VCDCredentials

    @property
    def type(self) -> CloudProviderType:
        return self._type


@dataclass(frozen=True)
class VolumeConfig:
    size_mb: int | None = None
    path: str | None = None


@dataclass(frozen=True)
class StorageConfig:
    url: URL
    volumes: Sequence[VolumeConfig] = ()


@dataclass(frozen=True)
class BlobStorageConfig:
    url: URL


@dataclass(frozen=True)
class RegistryConfig:
    url: URL


@dataclass(frozen=True)
class MonitoringConfig:
    url: URL


@dataclass(frozen=True)
class MetricsConfig:
    url: URL


@dataclass(frozen=True)
class SecretsConfig:
    url: URL


@dataclass(frozen=True)
class DisksConfig:
    url: URL
    storage_limit_per_user_gb: int


@dataclass(frozen=True)
class BucketsConfig:
    url: URL
    disable_creation: bool = False


class ACMEEnvironment(str, enum.Enum):
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass(frozen=True)
class IngressConfig:
    acme_environment: ACMEEnvironment
    cors_origins: Sequence[str] = ()


@dataclass(frozen=True)
class TPUResource:
    ipv4_cidr_block: str
    types: Sequence[str] = field(default_factory=list)
    software_versions: Sequence[str] = field(default_factory=list)


@dataclass(frozen=True)
class TPUPreset:
    type: str
    software_version: str


@dataclass(frozen=True)
class ResourcePreset:
    name: str
    credits_per_hour: Decimal
    cpu: float
    memory_mb: int
    gpu: int | None = None
    gpu_model: str | None = None
    tpu: TPUPreset | None = None
    scheduler_enabled: bool = False
    preemptible_node: bool = False
    resource_affinity: Sequence[str] = ()


@dataclass(frozen=True)
class ResourcePoolType:
    name: str
    min_size: int = 0
    max_size: int = 1
    idle_size: int = 0
    cpu: float = 1.0
    available_cpu: float = 1.0
    memory_mb: int = 1024
    available_memory_mb: int = 1024
    disk_size_gb: int = 150
    gpu: int | None = None
    gpu_model: str | None = None
    price: Decimal = Decimal()
    currency: str | None = None
    tpu: TPUResource | None = None
    is_preemptible: bool = False


@dataclass(frozen=True)
class Resources:
    cpu_m: int
    memory_mb: int
    gpu: int = 0


@dataclass(frozen=True)
class IdleJobConfig:
    count: int
    image: str
    resources: Resources
    image_secret: str = ""
    env: dict[str, str] = field(default_factory=dict)
    node_selector: dict[str, str] = field(default_factory=dict)


@dataclass
class OrchestratorConfig:
    job_hostname_template: str
    job_internal_hostname_template: str
    job_fallback_hostname: str
    job_schedule_timeout_s: float
    job_schedule_scale_up_timeout_s: float
    is_http_ingress_secure: bool = True
    resource_pool_types: Sequence[ResourcePoolType] = field(default_factory=list)
    resource_presets: Sequence[ResourcePreset] = field(default_factory=list)
    allow_privileged_mode: bool = False
    pre_pull_images: Sequence[str] = ()
    idle_jobs: Sequence[IdleJobConfig] = field(default_factory=list)


@dataclass
class ARecord:
    name: str
    ips: Sequence[str] = field(default_factory=list)
    dns_name: str = ""
    zone_id: str = ""
    evaluate_target_health: bool = False


@dataclass
class DNSConfig:
    name: str
    a_records: Sequence[ARecord] = field(default_factory=list)


@dataclass(frozen=True)
class Cluster:
    name: str
    orchestrator: OrchestratorConfig | None = None
    storage: StorageConfig | None = None
    blob_storage: BlobStorageConfig | None = None
    registry: RegistryConfig | None = None
    monitoring: MonitoringConfig | None = None
    secrets: SecretsConfig | None = None
    metrics: MetricsConfig | None = None
    dns: DNSConfig | None = None
    disks: DisksConfig | None = None
    buckets: BucketsConfig | None = None
    ingress: IngressConfig | None = None
    cloud_provider: CloudProvider | None = None
