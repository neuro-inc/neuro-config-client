from __future__ import annotations

import sys
from datetime import datetime, time, tzinfo
from decimal import Decimal
from typing import Any

from yarl import URL

from .entities import (
    AMDGPU,
    GPU,
    ACMEEnvironment,
    AMDGPUPreset,
    AppsConfig,
    ARecord,
    BucketsConfig,
    Cluster,
    CredentialsConfig,
    DisksConfig,
    DNSConfig,
    DockerRegistryConfig,
    EMCECSCredentials,
    EnergyConfig,
    EnergySchedule,
    EnergySchedulePeriod,
    GPUPreset,
    GrafanaCredentials,
    HelmRegistryConfig,
    IdleJobConfig,
    IngressConfig,
    IntelGPU,
    IntelGPUPreset,
    KubernetesCredentials,
    MetricsConfig,
    MinioCredentials,
    MonitoringConfig,
    NeuroAuthConfig,
    NvidiaGPU,
    NvidiaGPUPreset,
    NvidiaMigProfile,
    OpenStackCredentials,
    OrchestratorConfig,
    PatchClusterRequest,
    PatchOrchestratorConfigRequest,
    PrometheusCredentials,
    RegistryConfig,
    ResourcePoolType,
    ResourcePreset,
    Resources,
    SecretsConfig,
    SentryCredentials,
    StorageConfig,
    TPUPreset,
    TPUResource,
    VolumeConfig,
)

if sys.version_info >= (3, 9):
    from zoneinfo import ZoneInfo
else:
    # why not backports.zoneinfo: https://github.com/pganssle/zoneinfo/issues/125
    from backports.zoneinfo._zoneinfo import ZoneInfo


class EntityFactory:
    def create_cluster(self, payload: dict[str, Any]) -> Cluster:
        credentials = payload.get("credentials")
        timezone = self._create_timezone(payload.get("timezone"))
        return Cluster(
            name=payload["name"],
            location=payload.get("location"),
            logo_url=URL(logo_url) if (logo_url := payload.get("logo_url")) else None,
            orchestrator=self.create_orchestrator(payload["orchestrator"]),
            storage=self.create_storage(payload["storage"]),
            registry=self.create_registry(payload["registry"]),
            monitoring=self.create_monitoring(payload["monitoring"]),
            secrets=self.create_secrets(payload["secrets"]),
            metrics=self.create_metrics(payload["metrics"]),
            disks=self.create_disks(payload["disks"]),
            buckets=self.create_buckets(payload["buckets"]),
            ingress=self.create_ingress(payload["ingress"]),
            dns=self.create_dns(payload["dns"]),
            credentials=self.create_credentials(credentials) if credentials else None,
            created_at=datetime.fromisoformat(payload["created_at"]),
            timezone=timezone,
            energy=self.create_energy(payload["energy"], timezone=timezone),
            apps=self.create_apps(payload["apps"]),
        )

    def create_orchestrator(self, payload: dict[str, Any]) -> OrchestratorConfig:
        return OrchestratorConfig(
            job_hostname_template=payload["job_hostname_template"],
            job_fallback_hostname=payload["job_fallback_hostname"],
            job_schedule_timeout_s=payload["job_schedule_timeout_s"],
            job_schedule_scale_up_timeout_s=payload["job_schedule_scale_up_timeout_s"],
            is_http_ingress_secure=payload["is_http_ingress_secure"],
            resource_pool_types=[
                self.create_resource_pool_type(r)
                for r in payload.get("resource_pool_types", ())
            ],
            resource_presets=[
                self.create_resource_preset(preset)
                for preset in payload.get("resource_presets", ())
            ],
            allow_privileged_mode=payload.get(
                "allow_privileged_mode", OrchestratorConfig.allow_privileged_mode
            ),
            allow_job_priority=payload.get(
                "allow_job_priority", OrchestratorConfig.allow_job_priority
            ),
            pre_pull_images=payload.get("pre_pull_images", ()),
            idle_jobs=[
                self.create_idle_job(job) for job in payload.get("idle_jobs", ())
            ],
        )

    def create_resource_pool_type(self, payload: dict[str, Any]) -> ResourcePoolType:
        cpu = payload.get("cpu", ResourcePoolType.cpu)
        memory = payload.get("memory", ResourcePoolType.memory)
        disk_size = payload.get("disk_size", ResourcePoolType.disk_size)
        return ResourcePoolType(
            name=payload["name"],
            min_size=payload.get("min_size", ResourcePoolType.min_size),
            max_size=payload.get("max_size", ResourcePoolType.max_size),
            idle_size=payload.get("idle_size", ResourcePoolType.idle_size),
            cpu=cpu,
            available_cpu=payload.get("available_cpu") or cpu,
            memory=memory,
            available_memory=payload.get("available_memory") or memory,
            disk_size=disk_size,
            available_disk_size=payload.get("available_disk_size", disk_size),
            nvidia_gpu=(
                self._create_nvidia_gpu(nvidia_gpu)
                if (nvidia_gpu := payload.get("nvidia_gpu"))
                else None
            ),
            amd_gpu=(
                self._create_amd_gpu(amd_gpu)
                if (amd_gpu := payload.get("amd_gpu"))
                else None
            ),
            intel_gpu=(
                self._create_intel_gpu(intel_gpu)
                if (intel_gpu := payload.get("intel_gpu"))
                else None
            ),
            tpu=(
                self.create_tpu_resource(tpu) if (tpu := payload.get("tpu")) else None
            ),
            price=Decimal(payload.get("price", ResourcePoolType.price)),
            currency=payload.get("currency"),
            is_preemptible=payload.get(
                "is_preemptible", ResourcePoolType.is_preemptible
            ),
            cpu_min_watts=payload.get("cpu_min_watts", ResourcePoolType.cpu_min_watts),
            cpu_max_watts=payload.get("cpu_max_watts", ResourcePoolType.cpu_max_watts),
        )

    def _create_nvidia_gpu(self, payload: dict[str, Any]) -> NvidiaGPU:
        return NvidiaGPU(
            count=payload["count"],
            model=payload["model"],
            memory=payload.get("memory"),
            mig_profiles=[
                self._create_nvidia_mig_profile(mig)
                for mig in payload.get("mig_profiles", ())
            ],
        )

    def _create_nvidia_mig_profile(self, payload: dict[str, Any]) -> NvidiaMigProfile:
        return NvidiaMigProfile(
            name=payload["name"],
            count=payload["count"],
            model=payload["model"],
            memory=payload.get("memory"),
        )

    def _create_amd_gpu(self, payload: dict[str, Any]) -> AMDGPU:
        return AMDGPU(
            count=payload["count"],
            model=payload["model"],
            memory=payload.get("memory"),
        )

    def _create_intel_gpu(self, payload: dict[str, Any]) -> IntelGPU:
        return IntelGPU(
            count=payload["count"],
            model=payload["model"],
            memory=payload.get("memory"),
        )

    def create_tpu_resource(self, payload: dict[str, Any]) -> TPUResource:
        return TPUResource(
            ipv4_cidr_block=payload["ipv4_cidr_block"],
            types=list(payload["types"]),
            software_versions=list(payload["software_versions"]),
        )

    def create_resource_preset(self, payload: dict[str, Any]) -> ResourcePreset:
        return ResourcePreset(
            name=payload["name"],
            credits_per_hour=Decimal(payload["credits_per_hour"]),
            cpu=payload["cpu"],
            memory=payload["memory"],
            nvidia_gpu=(
                self._create_nvidia_gpu_preset(nvidia_gpu)
                if (nvidia_gpu := payload.get("nvidia_gpu"))
                else None
            ),
            amd_gpu=(
                self._create_amd_gpu_preset(amd_gpu)
                if (amd_gpu := payload.get("amd_gpu"))
                else None
            ),
            intel_gpu=(
                self._create_intel_gpu_preset(intel_gpu)
                if (intel_gpu := payload.get("intel_gpu"))
                else None
            ),
            tpu=self.create_tpu_preset(tpu) if (tpu := payload.get("tpu")) else None,
            scheduler_enabled=payload.get("scheduler_enabled", False),
            preemptible_node=payload.get("preemptible_node", False),
            is_external_job=payload.get("is_external_job", False),
            resource_pool_names=payload.get("resource_pool_names", ()),
            available_resource_pool_names=payload.get(
                "available_resource_pool_names", ()
            ),
            capacity=payload.get("capacity", 0),
        )

    def _create_nvidia_gpu_preset(self, payload: dict[str, Any]) -> NvidiaGPUPreset:
        return NvidiaGPUPreset(
            count=payload["count"],
            model=payload.get("model"),
            memory=payload.get("memory"),
            mig_profile=payload.get("mig_profile"),
        )

    def _create_amd_gpu_preset(self, payload: dict[str, Any]) -> AMDGPUPreset:
        return AMDGPUPreset(
            count=payload["count"],
            model=payload.get("model"),
            memory=payload.get("memory"),
        )

    def _create_intel_gpu_preset(self, payload: dict[str, Any]) -> IntelGPUPreset:
        return IntelGPUPreset(
            count=payload["count"],
            model=payload.get("model"),
            memory=payload.get("memory"),
        )

    def create_tpu_preset(self, payload: dict[str, Any]) -> TPUPreset:
        return TPUPreset(
            type=payload["type"], software_version=payload["software_version"]
        )

    def create_idle_job(self, payload: dict[str, Any]) -> IdleJobConfig:
        return IdleJobConfig(
            name=payload["name"],
            count=payload["count"],
            image=payload["image"],
            command=payload.get("command", []),
            args=payload.get("args", []),
            image_pull_secret=payload.get("image_pull_secret"),
            resources=self.create_resources(payload["resources"]),
            env=payload.get("env") or {},
            node_selector=payload.get("node_selector") or {},
        )

    def create_resources(self, payload: dict[str, Any]) -> Resources:
        return Resources(
            cpu=payload["cpu"],
            memory=payload["memory"],
            nvidia_gpu=payload.get("nvidia_gpu", 0),
            amd_gpu=payload.get("amd_gpu", 0),
            intel_gpu=payload.get("intel_gpu", 0),
        )

    def create_storage(self, payload: dict[str, Any]) -> StorageConfig:
        return StorageConfig(
            url=URL(payload["url"]),
            volumes=[self.create_volume(e) for e in payload.get("volumes", ())],
        )

    def create_volume(self, payload: dict[str, Any]) -> VolumeConfig:
        return VolumeConfig(
            name=payload["name"],
            path=payload.get("path"),
            size=payload.get("size"),
            credits_per_hour_per_gb=Decimal(
                payload.get(
                    "credits_per_hour_per_gb", VolumeConfig.credits_per_hour_per_gb
                )
            ),
        )

    def create_registry(self, payload: dict[str, Any]) -> RegistryConfig:
        return RegistryConfig(url=URL(payload["url"]))

    def create_monitoring(self, payload: dict[str, Any]) -> MonitoringConfig:
        return MonitoringConfig(url=URL(payload["url"]))

    def create_secrets(self, payload: dict[str, Any]) -> SecretsConfig:
        return SecretsConfig(url=URL(payload["url"]))

    def create_metrics(self, payload: dict[str, Any]) -> MetricsConfig:
        return MetricsConfig(url=URL(payload["url"]))

    def create_dns(self, payload: dict[str, Any]) -> DNSConfig:
        return DNSConfig(
            name=payload["name"],
            a_records=[self.create_a_record(r) for r in payload.get("a_records", ())],
        )

    def create_a_record(self, payload: dict[str, Any]) -> ARecord:
        return ARecord(
            name=payload["name"],
            ips=payload.get("ips", ()),
            dns_name=payload.get("dns_name", ARecord.dns_name),
            zone_id=payload.get("zone_id", ARecord.zone_id),
            evaluate_target_health=payload.get(
                "evaluate_target_health", ARecord.evaluate_target_health
            ),
        )

    def create_disks(self, payload: dict[str, Any]) -> DisksConfig:
        return DisksConfig(
            url=URL(payload["url"]),
            storage_limit_per_user=payload["storage_limit_per_user"],
        )

    def create_buckets(self, payload: dict[str, Any]) -> BucketsConfig:
        return BucketsConfig(
            url=URL(payload["url"]),
            disable_creation=payload.get("disable_creation", False),
        )

    def create_ingress(self, payload: dict[str, Any]) -> IngressConfig:
        return IngressConfig(
            acme_environment=ACMEEnvironment(payload["acme_environment"]),
            default_cors_origins=payload.get("default_cors_origins", ()),
            additional_cors_origins=payload.get("additional_cors_origins", ()),
        )

    @classmethod
    def create_credentials(
        cls, payload: dict[str, Any] | None
    ) -> CredentialsConfig | None:
        if not payload:
            return None
        kubernetes = payload.get("kubernetes")
        grafana = payload.get("grafana")
        prometheus = payload.get("prometheus")
        sentry = payload.get("sentry")
        docker_hub = payload.get("docker_hub")
        minio = payload.get("minio")
        emc_ecs = payload.get("emc_ecs")
        open_stack = payload.get("open_stack")
        return CredentialsConfig(
            neuro=cls._create_neuro_auth(payload["neuro"]),
            neuro_registry=cls._create_docker_registry(payload["neuro_registry"]),
            neuro_helm=cls._create_helm_registry(payload["neuro_helm"]),
            kubernetes=(
                cls._create_kubernetes_credentials(kubernetes) if kubernetes else None
            ),
            grafana=cls._create_grafana_credentials(grafana) if grafana else None,
            prometheus=(
                cls._create_promtheus_credentials(prometheus) if prometheus else None
            ),
            sentry=cls._create_sentry_credentials(sentry) if sentry else None,
            docker_hub=cls._create_docker_registry(docker_hub) if docker_hub else None,
            minio=cls._create_minio_credentials(minio) if minio else None,
            emc_ecs=cls._create_emc_ecs_credentials(emc_ecs) if emc_ecs else None,
            open_stack=(
                cls._create_open_stack_credentials(open_stack) if open_stack else None
            ),
        )

    @classmethod
    def _create_docker_registry(cls, payload: dict[str, Any]) -> DockerRegistryConfig:
        return DockerRegistryConfig(
            url=URL(payload["url"]),
            username=payload.get("username"),
            password=payload.get("password"),
            email=payload.get("email"),
        )

    @classmethod
    def _create_helm_registry(cls, payload: dict[str, Any]) -> HelmRegistryConfig:
        return HelmRegistryConfig(
            url=URL(payload["url"]),
            username=payload.get("username"),
            password=payload.get("password"),
        )

    @classmethod
    def _create_neuro_auth(cls, payload: dict[str, Any]) -> NeuroAuthConfig:
        return NeuroAuthConfig(
            url=URL(payload["url"]),
            token=payload["token"],
        )

    @classmethod
    def _create_kubernetes_credentials(
        self, payload: dict[str, Any]
    ) -> KubernetesCredentials:
        url = URL(payload["url"])
        ca_data = payload["ca_data"]
        if "token" in payload:
            return KubernetesCredentials(
                url=url,
                ca_data=ca_data,
                token=payload["token"],
            )
        if "client_key_data" in payload:
            return KubernetesCredentials(
                url=url,
                ca_data=ca_data,
                client_key_data=payload["client_key_data"],
                client_cert_data=payload["client_cert_data"],
            )
        return KubernetesCredentials(url=url, ca_data=ca_data)

    @classmethod
    def _create_grafana_credentials(cls, payload: dict[str, Any]) -> GrafanaCredentials:
        return GrafanaCredentials(
            username=payload["username"], password=payload["password"]
        )

    @classmethod
    def _create_promtheus_credentials(
        cls, payload: dict[str, Any]
    ) -> PrometheusCredentials:
        return PrometheusCredentials(
            username=payload["username"], password=payload["password"]
        )

    @classmethod
    def _create_sentry_credentials(cls, payload: dict[str, Any]) -> SentryCredentials:
        return SentryCredentials(
            client_key_id=payload["client_key_id"],
            public_dsn=URL(payload["public_dsn"]),
            sample_rate=payload.get("sample_rate", SentryCredentials.sample_rate),
        )

    @classmethod
    def _create_minio_credentials(cls, payload: dict[str, Any]) -> MinioCredentials:
        return MinioCredentials(
            username=payload["username"], password=payload["password"]
        )

    @classmethod
    def _create_emc_ecs_credentials(cls, payload: dict[str, Any]) -> EMCECSCredentials:
        return EMCECSCredentials(
            access_key_id=payload["access_key_id"],
            secret_access_key=payload["secret_access_key"],
            s3_endpoint=URL(payload["s3_endpoint"]),
            management_endpoint=URL(payload["management_endpoint"]),
            s3_assumable_role=payload["s3_assumable_role"],
        )

    @classmethod
    def _create_open_stack_credentials(
        cls, payload: dict[str, Any]
    ) -> OpenStackCredentials:
        return OpenStackCredentials(
            account_id=payload["account_id"],
            password=payload["password"],
            s3_endpoint=URL(payload["s3_endpoint"]),
            endpoint=URL(payload["endpoint"]),
            region_name=payload["region_name"],
        )

    def _create_timezone(self, name: str | None) -> tzinfo:
        if not name:
            return Cluster.timezone
        try:
            return ZoneInfo(name)
        except Exception:
            raise ValueError(f"invalid timezone: {name}")

    def create_energy(
        self, payload: dict[str, Any], *, timezone: tzinfo
    ) -> EnergyConfig:
        return EnergyConfig(
            co2_grams_eq_per_kwh=payload["co2_grams_eq_per_kwh"],
            schedules=[
                self._create_energy_schedule(s, timezone)
                for s in payload.get("schedules", ())
            ],
        )

    def _create_energy_schedule(
        self, payload: dict[str, Any], timezone: tzinfo
    ) -> EnergySchedule:
        return EnergySchedule(
            name=payload["name"],
            price_per_kwh=Decimal(payload["price_per_kwh"]),
            periods=[
                self._create_energy_schedule_period(p, timezone=timezone)
                for p in payload.get("periods", ())
            ],
        )

    def _create_energy_schedule_period(
        self, payload: dict[str, Any], *, timezone: tzinfo
    ) -> EnergySchedulePeriod:
        start_time = time.fromisoformat(payload["start_time"]).replace(tzinfo=timezone)
        end_time = time.fromisoformat(payload["end_time"]).replace(tzinfo=timezone)
        return EnergySchedulePeriod(
            weekday=payload["weekday"],
            start_time=start_time,
            end_time=end_time,
        )

    def create_apps(self, payload: dict[str, Any]) -> AppsConfig:
        return AppsConfig(
            apps_hostname_templates=payload.get("apps_hostname_templates", []),
            app_proxy_url=URL(payload["app_proxy_url"]),
        )


class PayloadFactory:
    @classmethod
    def create_patch_cluster_request(
        cls, request: PatchClusterRequest
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if request.location:
            payload["location"] = request.location
        if request.logo_url:
            payload["logo_url"] = str(request.logo_url)
        if request.credentials:
            payload["credentials"] = cls.create_credentials(request.credentials)
        if request.storage:
            payload["storage"] = cls.create_storage(request.storage)
        if request.registry:
            payload["registry"] = cls.create_registry(request.registry)
        if request.orchestrator:
            payload["orchestrator"] = cls.create_patch_orchestrator_request(
                request.orchestrator
            )
        if request.monitoring:
            payload["monitoring"] = cls.create_monitoring(request.monitoring)
        if request.secrets:
            payload["secrets"] = cls.create_secrets(request.secrets)
        if request.metrics:
            payload["metrics"] = cls.create_metrics(request.metrics)
        if request.disks:
            payload["disks"] = cls.create_disks(request.disks)
        if request.buckets:
            payload["buckets"] = cls.create_buckets(request.buckets)
        if request.ingress:
            payload["ingress"] = cls.create_ingress(request.ingress)
        if request.dns:
            payload["dns"] = cls.create_dns(request.dns)
        if request.timezone:
            payload["timezone"] = str(request.timezone)
        if request.energy:
            payload["energy"] = cls.create_energy(request.energy)
        if request.apps:
            payload["apps"] = cls.create_apps(request.apps)
        return payload

    @classmethod
    def create_credentials(cls, credentials: CredentialsConfig) -> dict[str, Any]:
        result = {
            "neuro": cls._create_neuro_auth(credentials.neuro),
            "neuro_helm": cls._create_helm_registry(credentials.neuro_helm),
            "neuro_registry": cls._create_docker_registry(credentials.neuro_registry),
        }
        if credentials.kubernetes is not None:
            result["kubernetes"] = cls._create_kubernetes_credentials(
                credentials.kubernetes
            )
        if credentials.grafana is not None:
            result["grafana"] = cls._create_grafana_credentials(credentials.grafana)
        if credentials.prometheus is not None:
            result["prometheus"] = cls._create_prometheus_credentials(
                credentials.prometheus
            )
        if credentials.sentry is not None:
            result["sentry"] = cls._create_sentry_credentials(credentials.sentry)
        if credentials.docker_hub is not None:
            result["docker_hub"] = cls._create_docker_registry(credentials.docker_hub)
        if credentials.minio is not None:
            result["minio"] = cls._create_minio_credentials(credentials.minio)
        if credentials.emc_ecs is not None:
            result["emc_ecs"] = cls._create_emc_ecs_credentials(credentials.emc_ecs)
        if credentials.open_stack is not None:
            result["open_stack"] = cls._create_open_stack_credentials(
                credentials.open_stack
            )
        return result

    @classmethod
    def _create_neuro_auth(cls, neuro_auth: NeuroAuthConfig) -> dict[str, Any]:
        return {"token": neuro_auth.token}

    @classmethod
    def _create_helm_registry(cls, helm_registry: HelmRegistryConfig) -> dict[str, Any]:
        result = {
            "username": helm_registry.username,
            "password": helm_registry.password,
        }
        return result

    @classmethod
    def _create_docker_registry(
        cls, docker_registry: DockerRegistryConfig
    ) -> dict[str, Any]:
        result = {
            "username": docker_registry.username,
            "password": docker_registry.password,
        }
        return result

    @classmethod
    def _create_grafana_credentials(
        cls, grafana_credentials: GrafanaCredentials
    ) -> dict[str, str]:
        result = {
            "username": grafana_credentials.username,
            "password": grafana_credentials.password,
        }
        return result

    @classmethod
    def _create_kubernetes_credentials(
        cls, kubernetes_credentials: KubernetesCredentials
    ) -> dict[str, str]:
        result = {
            "url": str(kubernetes_credentials.url),
            "ca_data": kubernetes_credentials.ca_data,
        }
        if kubernetes_credentials.token:
            result["token"] = kubernetes_credentials.token
        if (
            kubernetes_credentials.client_cert_data
            and kubernetes_credentials.client_key_data
        ):
            result["client_cert_data"] = kubernetes_credentials.client_cert_data
            result["client_key_data"] = kubernetes_credentials.client_key_data
        return result

    @classmethod
    def _create_prometheus_credentials(
        cls, prometheus_credentials: PrometheusCredentials
    ) -> dict[str, str]:
        return {
            "username": prometheus_credentials.username,
            "password": prometheus_credentials.password,
        }

    @classmethod
    def _create_sentry_credentials(
        cls, sentry_credentials: SentryCredentials
    ) -> dict[str, Any]:
        return {
            "client_key_id": sentry_credentials.client_key_id,
            "public_dsn": str(sentry_credentials.public_dsn),
            "sample_rate": sentry_credentials.sample_rate,
        }

    @classmethod
    def _create_minio_credentials(
        cls, minio_credentials: MinioCredentials
    ) -> dict[str, str]:
        result = {
            "username": minio_credentials.username,
            "password": minio_credentials.password,
        }
        return result

    @classmethod
    def _create_emc_ecs_credentials(
        cls, emc_ecs_credentials: EMCECSCredentials
    ) -> dict[str, str]:
        result = {
            "access_key_id": emc_ecs_credentials.access_key_id,
            "secret_access_key": emc_ecs_credentials.secret_access_key,
            "s3_endpoint": str(emc_ecs_credentials.s3_endpoint),
            "management_endpoint": str(emc_ecs_credentials.management_endpoint),
            "s3_assumable_role": emc_ecs_credentials.s3_assumable_role,
        }
        return result

    @classmethod
    def _create_open_stack_credentials(
        cls, open_stack_credentials: OpenStackCredentials
    ) -> dict[str, str]:
        result = {
            "account_id": open_stack_credentials.account_id,
            "password": open_stack_credentials.password,
            "endpoint": str(open_stack_credentials.endpoint),
            "s3_endpoint": str(open_stack_credentials.s3_endpoint),
            "region_name": open_stack_credentials.region_name,
        }
        return result

    @classmethod
    def create_storage(cls, storage: StorageConfig) -> dict[str, Any]:
        result: dict[str, Any] = {"url": str(storage.url)}
        if storage.volumes:
            result["volumes"] = [cls._create_volume(e) for e in storage.volumes]
        return result

    @classmethod
    def _create_volume(cls, volume: VolumeConfig) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": volume.name,
            "credits_per_hour_per_gb": str(volume.credits_per_hour_per_gb),
        }
        if volume.path:
            result["path"] = volume.path
        if volume.size is not None:
            result["size"] = volume.size
        return result

    @classmethod
    def create_registry(cls, registry: RegistryConfig) -> dict[str, Any]:
        return {"url": str(registry.url)}

    def create_orchestrator(self, orchestrator: OrchestratorConfig) -> dict[str, Any]:
        result = {
            "job_hostname_template": orchestrator.job_hostname_template,
            "is_http_ingress_secure": orchestrator.is_http_ingress_secure,
            "job_fallback_hostname": orchestrator.job_fallback_hostname,
            "job_schedule_timeout_s": orchestrator.job_schedule_timeout_s,
            "job_schedule_scale_up_timeout_s": (
                orchestrator.job_schedule_scale_up_timeout_s
            ),
        }
        if orchestrator.allow_privileged_mode:
            result["allow_privileged_mode"] = orchestrator.allow_privileged_mode
        if orchestrator.allow_job_priority:
            result["allow_job_priority"] = orchestrator.allow_job_priority
        if orchestrator.resource_pool_types:
            result["resource_pool_types"] = [
                self.create_resource_pool_type(r)
                for r in orchestrator.resource_pool_types
            ]
        if orchestrator.resource_presets:
            result["resource_presets"] = [
                self.create_resource_preset(preset)
                for preset in orchestrator.resource_presets
            ]
        if orchestrator.pre_pull_images:
            result["pre_pull_images"] = orchestrator.pre_pull_images
        if orchestrator.idle_jobs:
            result["idle_jobs"] = [
                self._create_idle_job(job) for job in orchestrator.idle_jobs
            ]
        return result

    @classmethod
    def create_patch_orchestrator_request(
        cls, orchestrator: PatchOrchestratorConfigRequest
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if orchestrator.job_hostname_template:
            payload["job_hostname_template"] = orchestrator.job_hostname_template
        if orchestrator.is_http_ingress_secure is not None:
            payload["is_http_ingress_secure"] = orchestrator.is_http_ingress_secure
        if orchestrator.job_fallback_hostname:
            payload["job_fallback_hostname"] = orchestrator.job_fallback_hostname
        if orchestrator.job_schedule_timeout_s is not None:
            payload["job_schedule_timeout_s"] = orchestrator.job_schedule_timeout_s
        if orchestrator.job_schedule_scale_up_timeout_s is not None:
            payload["job_schedule_scale_up_timeout_s"] = (
                orchestrator.job_schedule_scale_up_timeout_s
            )
        if orchestrator.allow_privileged_mode is not None:
            payload["allow_privileged_mode"] = orchestrator.allow_privileged_mode
        if orchestrator.allow_job_priority is not None:
            payload["allow_job_priority"] = orchestrator.allow_job_priority
        if orchestrator.resource_pool_types:
            payload["resource_pool_types"] = [
                cls.create_resource_pool_type(r)
                for r in orchestrator.resource_pool_types
            ]
        if orchestrator.resource_presets:
            payload["resource_presets"] = [
                cls.create_resource_preset(preset)
                for preset in orchestrator.resource_presets
            ]
        if orchestrator.pre_pull_images:
            payload["pre_pull_images"] = orchestrator.pre_pull_images
        if orchestrator.idle_jobs:
            payload["idle_jobs"] = [
                cls._create_idle_job(job) for job in orchestrator.idle_jobs
            ]
        return payload

    @classmethod
    def create_resource_pool_type(
        cls, resource_pool_type: ResourcePoolType
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": resource_pool_type.name,
            "is_preemptible": resource_pool_type.is_preemptible,
            "min_size": resource_pool_type.min_size,
            "max_size": resource_pool_type.max_size,
            "idle_size": resource_pool_type.idle_size,
            "cpu": resource_pool_type.cpu,
            "available_cpu": resource_pool_type.available_cpu,
            "memory": resource_pool_type.memory,
            "available_memory": resource_pool_type.available_memory,
            "disk_size": resource_pool_type.disk_size,
            "available_disk_size": resource_pool_type.available_disk_size,
        }
        if resource_pool_type.nvidia_gpu:
            result["nvidia_gpu"] = cls._create_nvidia_gpu(resource_pool_type.nvidia_gpu)
        if resource_pool_type.amd_gpu:
            result["amd_gpu"] = cls._create_gpu(resource_pool_type.amd_gpu)
        if resource_pool_type.intel_gpu:
            result["intel_gpu"] = cls._create_gpu(resource_pool_type.intel_gpu)
        if resource_pool_type.currency:
            result["price"] = str(resource_pool_type.price)
            result["currency"] = resource_pool_type.currency
        if resource_pool_type.tpu:
            result["tpu"] = cls.create_tpu_resource(resource_pool_type.tpu)
        if resource_pool_type.cpu_min_watts:
            result["cpu_min_watts"] = resource_pool_type.cpu_min_watts
        if resource_pool_type.cpu_max_watts:
            result["cpu_max_watts"] = resource_pool_type.cpu_max_watts
        return result

    @classmethod
    def _create_nvidia_gpu(cls, gpu: NvidiaGPU) -> dict[str, Any]:
        result = cls._create_gpu(gpu)
        if gpu.mig_profiles:
            result["mig_profiles"] = [
                cls._create_nvidia_mig_profile(profile) for profile in gpu.mig_profiles
            ]
        return result

    @classmethod
    def _create_nvidia_mig_profile(
        cls, mig_profile: NvidiaMigProfile
    ) -> dict[str, Any]:
        result = {
            "name": mig_profile.name,
            "count": mig_profile.count,
            "model": mig_profile.model,
        }
        if mig_profile.memory:
            result["memory"] = mig_profile.memory
        return result

    @classmethod
    def _create_gpu(cls, gpu: GPU) -> dict[str, Any]:
        result: dict[str, Any] = {
            "count": gpu.count,
            "model": gpu.model,
        }
        if gpu.memory:
            result["memory"] = gpu.memory
        return result

    @classmethod
    def create_tpu_resource(cls, tpu: TPUResource) -> dict[str, Any]:
        return {
            "ipv4_cidr_block": tpu.ipv4_cidr_block,
            "types": list(tpu.types),
            "software_versions": list(tpu.software_versions),
        }

    @classmethod
    def create_resource_preset(cls, preset: ResourcePreset) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": preset.name,
            "credits_per_hour": str(preset.credits_per_hour),
            "cpu": preset.cpu,
            "memory": preset.memory,
        }
        if preset.nvidia_gpu:
            result["nvidia_gpu"] = cls._create_nvidia_gpu_preset(preset.nvidia_gpu)
        if preset.amd_gpu:
            result["amd_gpu"] = cls._create_gpu_preset(preset.amd_gpu)
        if preset.intel_gpu:
            result["intel_gpu"] = cls._create_gpu_preset(preset.intel_gpu)
        if preset.tpu:
            result["tpu"] = cls._create_tpu_preset(preset.tpu)
        if preset.scheduler_enabled:
            result["scheduler_enabled"] = preset.scheduler_enabled
        if preset.preemptible_node:
            result["preemptible_node"] = preset.preemptible_node
        if preset.resource_pool_names:
            result["resource_pool_names"] = preset.resource_pool_names
        return result

    @classmethod
    def _create_nvidia_gpu_preset(cls, gpu_preset: NvidiaGPUPreset) -> dict[str, Any]:
        result = cls._create_gpu_preset(gpu_preset)
        if gpu_preset.mig_profile:
            result["mig_profile"] = gpu_preset.mig_profile
        return result

    @classmethod
    def _create_gpu_preset(cls, gpu_preset: GPUPreset) -> dict[str, Any]:
        result: dict[str, Any] = {"count": gpu_preset.count}
        if gpu_preset.model:
            result["model"] = gpu_preset.model
        return result

    @classmethod
    def _create_tpu_preset(cls, tpu: TPUPreset) -> dict[str, Any]:
        return {"type": tpu.type, "software_version": tpu.software_version}

    @classmethod
    def _create_idle_job(cls, idle_job: IdleJobConfig) -> dict[str, Any]:
        result = {
            "name": idle_job.name,
            "count": idle_job.count,
            "image": idle_job.image,
            "resources": cls._create_resources(idle_job.resources),
        }
        if idle_job.command:
            result["command"] = idle_job.command
        if idle_job.args:
            result["args"] = idle_job.args
        if idle_job.image_pull_secret:
            result["image_pull_secret"] = idle_job.image_pull_secret
        if idle_job.env:
            result["env"] = idle_job.env
        if idle_job.node_selector:
            result["node_selector"] = idle_job.node_selector
        return result

    @classmethod
    def _create_resources(cls, resources: Resources) -> dict[str, Any]:
        result = {"cpu": resources.cpu, "memory": resources.memory}
        if resources.nvidia_gpu:
            result["nvidia_gpu"] = resources.nvidia_gpu
        if resources.amd_gpu:
            result["amd_gpu"] = resources.amd_gpu
        if resources.intel_gpu:
            result["intel_gpu"] = resources.intel_gpu
        return result

    @classmethod
    def create_monitoring(cls, monitoring: MonitoringConfig) -> dict[str, Any]:
        return {"url": str(monitoring.url)}

    @classmethod
    def create_metrics(cls, metrics: MetricsConfig) -> dict[str, Any]:
        return {"url": str(metrics.url)}

    @classmethod
    def create_secrets(cls, secrets: SecretsConfig) -> dict[str, Any]:
        return {"url": str(secrets.url)}

    @classmethod
    def create_buckets(cls, buckets: BucketsConfig) -> dict[str, Any]:
        return {"url": str(buckets.url), "disable_creation": buckets.disable_creation}

    @classmethod
    def create_dns(cls, dns: DNSConfig) -> dict[str, Any]:
        result: dict[str, Any] = {"name": dns.name}
        if dns.a_records:
            result["a_records"] = [cls.create_a_record(r) for r in dns.a_records]
        return result

    @classmethod
    def create_a_record(cls, a_record: ARecord) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": a_record.name,
        }
        if a_record.ips:
            result["ips"] = a_record.ips
        if a_record.dns_name:
            result["dns_name"] = a_record.dns_name
        if a_record.zone_id:
            result["zone_id"] = a_record.zone_id
        if a_record.evaluate_target_health:
            result["evaluate_target_health"] = a_record.evaluate_target_health
        return result

    @classmethod
    def create_disks(cls, disks: DisksConfig) -> dict[str, Any]:
        return {
            "url": str(disks.url),
            "storage_limit_per_user": disks.storage_limit_per_user,
        }

    @classmethod
    def create_ingress(cls, ingress: IngressConfig) -> dict[str, Any]:
        result: dict[str, Any] = {"acme_environment": ingress.acme_environment.value}
        if ingress.additional_cors_origins:
            result["additional_cors_origins"] = ingress.additional_cors_origins
        return result

    @classmethod
    def create_energy(cls, energy: EnergyConfig) -> dict[str, Any]:
        return {
            "co2_grams_eq_per_kwh": energy.co2_grams_eq_per_kwh,
            "schedules": [cls._create_energy_schedule(s) for s in energy.schedules],
        }

    @classmethod
    def _create_energy_schedule(cls, schedule: EnergySchedule) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": schedule.name,
            "price_per_kwh": str(schedule.price_per_kwh),
        }
        periods = [cls._create_energy_schedule_period(p) for p in schedule.periods]
        if periods:
            payload["periods"] = periods
        return payload

    @classmethod
    def _create_energy_schedule_period(
        cls, period: EnergySchedulePeriod
    ) -> dict[str, Any]:
        return {
            "weekday": period.weekday,
            "start_time": period.start_time.strftime("%H:%M"),
            "end_time": period.end_time.strftime("%H:%M"),
        }

    @classmethod
    def create_apps(cls, apps: AppsConfig) -> dict[str, Any]:
        return {
            "apps_hostname_templates": apps.apps_hostname_templates,
            "app_proxy_url": str(apps.app_proxy_url),
        }
