"""Platform config client."""
from pkg_resources import get_distribution

from .client import ConfigClient
from .entities import (
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
    CloudProvider,
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
    MetricsConfig,
    MinioCredentials,
    MonitoringConfig,
    NeuroAuthConfig,
    NodePool,
    NodePoolTemplate,
    NodeRole,
    NotificationType,
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

__all__ = [
    "ConfigClient",
    "ACMEEnvironment",
    "ARecord",
    "AWSCloudProvider",
    "AWSCredentials",
    "AWSStorage",
    "AzureCloudProvider",
    "AzureCredentials",
    "AzureReplicationType",
    "AzureStorage",
    "AzureStorageTier",
    "BucketsConfig",
    "CloudProvider",
    "CloudProviderType",
    "Cluster",
    "ClusterLocationType",
    "ClusterStatus",
    "CredentialsConfig",
    "DisksConfig",
    "DNSConfig",
    "DockerRegistryConfig",
    "EFSPerformanceMode",
    "EFSThroughputMode",
    "EMCECSCredentials",
    "GoogleCloudProvider",
    "GoogleFilestoreTier",
    "GoogleStorage",
    "GrafanaCredentials",
    "HelmRegistryConfig",
    "IdleJobConfig",
    "IngressConfig",
    "MetricsConfig",
    "MinioCredentials",
    "MonitoringConfig",
    "NeuroAuthConfig",
    "NodePool",
    "NodePoolTemplate",
    "NodeRole",
    "NotificationType",
    "OnPremCloudProvider",
    "OpenStackCredentials",
    "OrchestratorConfig",
    "RegistryConfig",
    "ResourcePoolType",
    "ResourcePreset",
    "Resources",
    "SecretsConfig",
    "SentryCredentials",
    "StorageConfig",
    "StorageInstance",
    "TPUPreset",
    "TPUResource",
    "VCDCloudProvider",
    "VCDCredentials",
    "VCDStorage",
    "VolumeConfig",
]
__version__ = get_distribution(__name__).version
