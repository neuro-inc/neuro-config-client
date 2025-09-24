from __future__ import annotations

import enum
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, time, tzinfo
from decimal import Decimal

from yarl import URL

if sys.version_info >= (3, 9):
    from zoneinfo import ZoneInfo
else:
    # why not backports.zoneinfo: https://github.com/pganssle/zoneinfo/issues/125
    from backports.zoneinfo._zoneinfo import ZoneInfo


class NotificationType(str, enum.Enum):
    SUCCESS = "success"
    ERROR = "error"
    CLUSTER_UPDATING = "cluster_updating"
    CLUSTER_UPDATE_SUCCEEDED = "cluster_update_succeeded"
    CLUSTER_UPDATE_FAILED = "cluster_update_failed"


@dataclass(frozen=True)
class KubernetesCredentials:
    url: URL
    ca_data: str
    token: str | None = field(repr=False, default=None)
    client_key_data: str | None = field(repr=False, default=None)
    client_cert_data: str | None = field(repr=False, default=None)


@dataclass(frozen=True)
class NeuroAuthConfig:
    url: URL
    token: str = field(repr=False)


@dataclass(frozen=True)
class HelmRegistryConfig:
    url: URL
    username: str | None = None
    password: str | None = field(repr=False, default=None)


@dataclass(frozen=True)
class DockerRegistryConfig:
    url: URL
    username: str | None = None
    password: str | None = field(repr=False, default=None)
    email: str | None = None


@dataclass(frozen=True)
class GrafanaCredentials:
    username: str
    password: str = field(repr=False)


@dataclass(frozen=True)
class PrometheusCredentials:
    username: str
    password: str = field(repr=False)


@dataclass(frozen=True)
class SentryCredentials:
    client_key_id: str
    public_dsn: URL
    sample_rate: float = 0.01


@dataclass(frozen=True)
class MinioCredentials:
    username: str
    password: str = field(repr=False)


@dataclass(frozen=True)
class EMCECSCredentials:
    """
    Credentials to EMC ECS (blob storage engine developed by vmware creators)
    """

    access_key_id: str
    secret_access_key: str = field(repr=False)
    s3_endpoint: URL
    management_endpoint: URL
    s3_assumable_role: str


@dataclass(frozen=True)
class OpenStackCredentials:
    account_id: str
    password: str = field(repr=False)
    endpoint: URL
    s3_endpoint: URL
    region_name: str


@dataclass(frozen=True)
class CredentialsConfig:
    neuro: NeuroAuthConfig
    neuro_helm: HelmRegistryConfig
    neuro_registry: DockerRegistryConfig
    kubernetes: KubernetesCredentials | None = None
    grafana: GrafanaCredentials | None = None
    prometheus: PrometheusCredentials | None = None
    sentry: SentryCredentials | None = None
    docker_hub: DockerRegistryConfig | None = None
    minio: MinioCredentials | None = None
    emc_ecs: EMCECSCredentials | None = None
    open_stack: OpenStackCredentials | None = None


@dataclass(frozen=True)
class VolumeConfig:
    name: str
    size: int | None = None
    path: str | None = None
    credits_per_hour_per_gb: Decimal = Decimal(0)


@dataclass(frozen=True)
class StorageConfig:
    url: URL
    volumes: Sequence[VolumeConfig] = ()


@dataclass(frozen=True)
class RegistryConfig:
    url: URL

    @property
    def host(self) -> str:
        """Returns registry hostname with port (if specified)"""
        port = self.url.explicit_port
        suffix = f":{port}" if port is not None else ""
        return f"{self.url.host}{suffix}"


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
    storage_limit_per_user: int


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
    default_cors_origins: Sequence[str] = ()
    additional_cors_origins: Sequence[str] = ()


@dataclass(frozen=True)
class GPUPreset:
    count: int
    model: str | None = None
    memory: int | None = None


@dataclass(frozen=True)
class NvidiaGPUPreset(GPUPreset):
    mig_profile: str | None = None


@dataclass(frozen=True)
class AMDGPUPreset(GPUPreset):
    pass


@dataclass(frozen=True)
class IntelGPUPreset(GPUPreset):
    pass


@dataclass(frozen=True)
class TPUPreset:
    type: str
    software_version: str


@dataclass(frozen=True)
class ResourcePreset:
    name: str
    credits_per_hour: Decimal
    cpu: float
    memory: int
    nvidia_gpu: NvidiaGPUPreset | None = None
    amd_gpu: AMDGPUPreset | None = None
    intel_gpu: IntelGPUPreset | None = None
    tpu: TPUPreset | None = None
    scheduler_enabled: bool = False
    preemptible_node: bool = False
    is_external_job: bool = False
    resource_pool_names: Sequence[str] = ()
    available_resource_pool_names: Sequence[str] = ()
    capacity: int = 0


@dataclass(frozen=True)
class GPU:
    count: int
    model: str
    memory: int | None = None


@dataclass(frozen=True)
class NvidiaMigProfile:
    name: str
    count: int
    model: str
    memory: int | None = None


@dataclass(frozen=True)
class NvidiaGPU(GPU):
    mig_profiles: Sequence[NvidiaMigProfile] = field(default_factory=list)


@dataclass(frozen=True)
class AMDGPU(GPU):
    pass


@dataclass(frozen=True)
class IntelGPU(GPU):
    pass


@dataclass(frozen=True)
class TPUResource:
    ipv4_cidr_block: str
    types: Sequence[str] = ()
    software_versions: Sequence[str] = ()


@dataclass(frozen=True)
class ResourcePoolType:
    name: str
    min_size: int = 0
    max_size: int = 1
    idle_size: int = 0

    cpu: float = 1.0
    available_cpu: float = 1.0
    memory: int = 2**30  # 1gb
    available_memory: int = 2**30
    disk_size: int = 150 * 2**30  # 150gb
    available_disk_size: int = 150 * 2**30  # 150gb

    nvidia_gpu: NvidiaGPU | None = None
    amd_gpu: AMDGPU | None = None
    intel_gpu: IntelGPU | None = None
    tpu: TPUResource | None = None

    price: Decimal = Decimal()
    currency: str | None = None

    is_preemptible: bool = False

    cpu_min_watts: float = 0.0
    cpu_max_watts: float = 0.0

    @property
    def has_gpu(self) -> bool:
        return any((self.nvidia_gpu, self.amd_gpu, self.intel_gpu))


@dataclass(frozen=True)
class Resources:
    cpu: float
    memory: int
    nvidia_gpu: int = 0
    amd_gpu: int = 0
    intel_gpu: int = 0


@dataclass(frozen=True)
class IdleJobConfig:
    name: str
    count: int
    image: str
    resources: Resources
    command: list[str] = field(default_factory=list)
    args: list[str] = field(default_factory=list)
    image_pull_secret: str | None = None
    env: dict[str, str] = field(default_factory=dict)
    node_selector: dict[str, str] = field(default_factory=dict)


@dataclass
class OrchestratorConfig:
    job_hostname_template: str
    job_fallback_hostname: str
    job_schedule_timeout_s: float = 300
    job_schedule_scale_up_timeout_s: float = 300
    is_http_ingress_secure: bool = True
    resource_pool_types: Sequence[ResourcePoolType] = ()
    resource_presets: Sequence[ResourcePreset] = ()
    allow_privileged_mode: bool = False
    allow_job_priority: bool = False
    pre_pull_images: Sequence[str] = ()
    idle_jobs: Sequence[IdleJobConfig] = ()

    @property
    def allow_scheduler_enabled_job(self) -> bool:
        for preset in self.resource_presets:
            if preset.scheduler_enabled:
                return True
        return False

    @property
    def tpu_resources(self) -> Sequence[TPUResource]:
        return tuple(
            resource.tpu for resource in self.resource_pool_types if resource.tpu
        )

    @property
    def tpu_ipv4_cidr_block(self) -> str | None:
        tpus = self.tpu_resources
        if not tpus:
            return None
        return tpus[0].ipv4_cidr_block


@dataclass
class PatchOrchestratorConfigRequest:
    job_hostname_template: str | None = None
    job_fallback_hostname: str | None = None
    job_schedule_timeout_s: float | None = None
    job_schedule_scale_up_timeout_s: float | None = None
    is_http_ingress_secure: bool | None = None
    resource_pool_types: Sequence[ResourcePoolType] | None = None
    resource_presets: Sequence[ResourcePreset] | None = None
    allow_privileged_mode: bool | None = None
    allow_job_priority: bool | None = None
    pre_pull_images: Sequence[str] | None = None
    idle_jobs: Sequence[IdleJobConfig] | None = None


@dataclass
class ARecord:
    name: str
    ips: Sequence[str] = ()
    dns_name: str | None = None
    zone_id: str | None = None
    evaluate_target_health: bool = False


@dataclass
class DNSConfig:
    name: str
    a_records: Sequence[ARecord] = ()


@dataclass(frozen=True)
class EnergySchedulePeriod:
    # ISO 8601 weekday number (1-7)
    weekday: int
    start_time: time
    end_time: time

    @classmethod
    def create_full_day(cls, *, weekday: int, timezone: tzinfo) -> EnergySchedulePeriod:
        return cls(
            weekday=weekday,
            start_time=time.min.replace(tzinfo=timezone),
            end_time=time.max.replace(tzinfo=timezone),
        )


DEFAULT_ENERGY_SCHEDULE_NAME = "default"


@dataclass(frozen=True)
class EnergySchedule:
    name: str
    periods: Sequence[EnergySchedulePeriod] = ()
    price_per_kwh: Decimal = Decimal("0")

    @classmethod
    def create_default(
        cls, *, timezone: tzinfo, name: str = DEFAULT_ENERGY_SCHEDULE_NAME
    ) -> EnergySchedule:
        return cls(
            name=name,
            periods=[
                EnergySchedulePeriod.create_full_day(weekday=weekday, timezone=timezone)
                for weekday in range(1, 8)
            ],
        )

    def check_time(self, current_time: datetime) -> bool:
        return any(self._is_time_within_period(current_time, p) for p in self.periods)

    def _is_time_within_period(
        self, time_: datetime, period: EnergySchedulePeriod
    ) -> bool:
        time_ = time_.astimezone(period.start_time.tzinfo)
        return (
            period.weekday == time_.isoweekday()
            and period.start_time <= time_.timetz() < period.end_time
        )


@dataclass(frozen=True)
class EnergyConfig:
    co2_grams_eq_per_kwh: float = 0
    schedules: Sequence[EnergySchedule] = ()

    def get_schedule(self, name: str) -> EnergySchedule:
        return (
            self._get_schedule(name)
            or self._get_schedule(DEFAULT_ENERGY_SCHEDULE_NAME)
            or EnergySchedule.create_default(timezone=ZoneInfo("UTC"))
        )

    def _get_schedule(self, name: str) -> EnergySchedule | None:
        for schedule in self.schedules:
            if schedule.name == name:
                return schedule
        return None

    @property
    def schedule_names(self) -> list[str]:
        return [schedule.name for schedule in self.schedules]


@dataclass(frozen=True)
class AppsConfig:
    apps_hostname_templates: list[str]
    app_proxy_url: URL


@dataclass(frozen=True)
class Cluster:
    name: str
    created_at: datetime
    orchestrator: OrchestratorConfig
    storage: StorageConfig
    registry: RegistryConfig
    monitoring: MonitoringConfig
    secrets: SecretsConfig
    metrics: MetricsConfig
    dns: DNSConfig
    disks: DisksConfig
    buckets: BucketsConfig
    ingress: IngressConfig
    energy: EnergyConfig
    apps: AppsConfig
    location: str | None = None
    logo_url: URL | None = None
    timezone: tzinfo = ZoneInfo("UTC")
    credentials: CredentialsConfig | None = None


@dataclass(frozen=True)
class PatchClusterRequest:
    location: str | None = None
    logo_url: URL | None = None
    credentials: CredentialsConfig | None = None
    storage: StorageConfig | None = None
    registry: RegistryConfig | None = None
    orchestrator: PatchOrchestratorConfigRequest | None = None
    monitoring: MonitoringConfig | None = None
    secrets: SecretsConfig | None = None
    metrics: MetricsConfig | None = None
    disks: DisksConfig | None = None
    buckets: BucketsConfig | None = None
    ingress: IngressConfig | None = None
    dns: DNSConfig | None = None
    timezone: ZoneInfo | None = None
    energy: EnergyConfig | None = None
    apps: AppsConfig | None = None
