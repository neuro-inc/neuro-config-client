from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from yarl import URL

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
    GoogleStorageBackend,
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
    NodeRole,
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


class EntityFactory:
    def create_cluster(self, payload: dict[str, Any]) -> Cluster:
        orchestrator = payload.get("orchestrator")
        storage = payload.get("storage")
        registry = payload.get("registry")
        monitoring = payload.get("monitoring")
        secrets = payload.get("secrets")
        metrics = payload.get("metrics")
        disks = payload.get("disks")
        buckets = payload.get("buckets")
        ingress = payload.get("ingress")
        dns = payload.get("dns")
        cloud_provider = payload.get("cloud_provider")
        credentials = payload.get("credentials")
        return Cluster(
            name=payload["name"],
            status=ClusterStatus(payload["status"]),
            platform_infra_image_tag=payload.get("platform_infra_image_tag"),
            orchestrator=self.create_orchestrator(orchestrator)
            if orchestrator
            else None,
            storage=self.create_storage(storage) if storage else None,
            registry=self.create_registry(registry) if registry else None,
            monitoring=self.create_monitoring(monitoring) if monitoring else None,
            secrets=self.create_secrets(secrets) if secrets else None,
            metrics=self.create_metrics(metrics) if metrics else None,
            disks=self.create_disks(disks) if disks else None,
            buckets=self.create_buckets(buckets) if buckets else None,
            ingress=self.create_ingress(ingress) if ingress else None,
            dns=self.create_dns(dns) if dns else None,
            cloud_provider=self.create_cloud_provider(cloud_provider)
            if cloud_provider
            else None,
            credentials=self.create_credentials(credentials) if credentials else None,
            created_at=datetime.fromisoformat(payload["created_at"]),
        )

    def create_orchestrator(self, payload: dict[str, Any]) -> OrchestratorConfig:
        return OrchestratorConfig(
            job_hostname_template=payload["job_hostname_template"],
            job_internal_hostname_template=payload.get(
                "job_internal_hostname_template"
            ),
            job_fallback_hostname=payload["job_fallback_hostname"],
            job_schedule_timeout_s=payload["job_schedule_timeout_s"],
            job_schedule_scale_up_timeout_s=payload["job_schedule_scale_up_timeout_s"],
            is_http_ingress_secure=payload["is_http_ingress_secure"],
            resource_pool_types=[
                self.create_resource_pool_type(r)
                for r in payload.get("resource_pool_types", [])
            ],
            resource_presets=[
                self.create_resource_preset(preset)
                for preset in payload.get("resource_presets", [])
            ],
            allow_privileged_mode=payload["allow_privileged_mode"],
            pre_pull_images=payload.get("pre_pull_images", ()),
            idle_jobs=[
                self.create_idle_job(job) for job in payload.get("idle_jobs", ())
            ],
        )

    def create_resource_pool_type(self, payload: dict[str, Any]) -> ResourcePoolType:
        tpu = None
        if payload.get("tpu"):
            tpu = self.create_tpu_resource(payload["tpu"])
        return ResourcePoolType(
            name=payload["name"],
            min_size=payload.get("min_size", ResourcePoolType.min_size),
            max_size=payload.get("max_size", ResourcePoolType.max_size),
            idle_size=payload.get("idle_size", ResourcePoolType.idle_size),
            cpu=payload.get("cpu", ResourcePoolType.cpu),
            available_cpu=payload.get("available_cpu", ResourcePoolType.available_cpu),
            memory_mb=payload.get("memory_mb", ResourcePoolType.memory_mb),
            available_memory_mb=payload.get(
                "available_memory_mb", ResourcePoolType.available_memory_mb
            ),
            gpu=payload.get("gpu"),
            gpu_model=payload.get("gpu_model"),
            price=Decimal(payload.get("price", ResourcePoolType.price)),
            currency=payload.get("currency"),
            tpu=tpu,
            is_preemptible=payload.get(
                "is_preemptible", ResourcePoolType.is_preemptible
            ),
        )

    def create_tpu_resource(self, payload: dict[str, Any]) -> TPUResource:
        return TPUResource(
            ipv4_cidr_block=payload["ipv4_cidr_block"],
            types=list(payload["types"]),
            software_versions=list(payload["software_versions"]),
        )

    def create_resource_preset(self, payload: dict[str, Any]) -> ResourcePreset:
        tpu = None
        if payload.get("tpu"):
            tpu = self.create_tpu_preset(payload["tpu"])
        return ResourcePreset(
            name=payload["name"],
            credits_per_hour=Decimal(payload["credits_per_hour"]),
            cpu=payload["cpu"],
            memory_mb=payload["memory_mb"],
            gpu=payload.get("gpu"),
            gpu_model=payload.get("gpu_model"),
            tpu=tpu,
            scheduler_enabled=payload.get("scheduler_enabled", False),
            preemptible_node=payload.get("preemptible_node", False),
            resource_affinity=payload.get("resource_affinity", ()),
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
            image_pull_secret=payload.get("image_pull_secret", ""),
            resources=self.create_resources(payload["resources"]),
            env=payload.get("env") or {},
            node_selector=payload.get("node_selector") or {},
        )

    def create_resources(self, payload: dict[str, Any]) -> Resources:
        return Resources(
            cpu_m=payload["cpu_m"],
            memory_mb=payload["memory_mb"],
            gpu=payload.get("gpu", 0),
        )

    def create_storage(self, payload: dict[str, Any]) -> StorageConfig:
        return StorageConfig(
            url=URL(payload["url"]),
            volumes=[self.create_volume(e) for e in payload.get("volumes", ())],
        )

    def create_volume(self, payload: dict[str, Any]) -> VolumeConfig:
        return VolumeConfig(path=payload.get("path"), size_mb=payload.get("size_mb"))

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
            a_records=[self.create_a_record(r) for r in payload.get("a_records", [])],
        )

    def create_a_record(self, payload: dict[str, Any]) -> ARecord:
        return ARecord(
            name=payload["name"],
            ips=payload.get("ips", []),
            dns_name=payload.get("dns_name", ARecord.dns_name),
            zone_id=payload.get("zone_id", ARecord.zone_id),
            evaluate_target_health=payload.get(
                "evaluate_target_health", ARecord.evaluate_target_health
            ),
        )

    def create_disks(self, payload: dict[str, Any]) -> DisksConfig:
        return DisksConfig(
            url=URL(payload["url"]),
            storage_limit_per_user_gb=payload["storage_limit_per_user_gb"],
        )

    def create_buckets(self, payload: dict[str, Any]) -> BucketsConfig:
        return BucketsConfig(
            url=URL(payload["url"]),
            disable_creation=payload.get("disable_creation", False),
        )

    def create_ingress(self, payload: dict[str, Any]) -> IngressConfig:
        return IngressConfig(
            acme_environment=ACMEEnvironment(payload["acme_environment"]),
            cors_origins=payload.get("cors_origins", ()),
        )

    def create_cloud_provider(self, payload: dict[str, Any]) -> CloudProvider:
        cp_type = CloudProviderType(payload["type"].lower())
        if cp_type == CloudProviderType.AWS:
            return self._create_aws_cloud_provider(payload)
        elif cp_type == CloudProviderType.GCP:
            return self._create_google_cloud_provider(payload)
        elif cp_type == CloudProviderType.AZURE:
            return self._create_azure_cloud_provider(payload)
        elif cp_type == CloudProviderType.ON_PREM:
            return self._create_on_prem_cloud_provider(payload)
        elif cp_type.startswith("vcd_"):
            return self._create_vcd_cloud_provider(payload)
        raise ValueError(f"Cloud provider '{cp_type}' is not supported")

    def _create_aws_cloud_provider(self, payload: dict[str, Any]) -> CloudProvider:
        credentials = payload["credentials"]
        return AWSCloudProvider(
            region=payload["region"],
            zones=payload["zones"],
            vpc_id=payload.get("vpc_id"),
            credentials=AWSCredentials(
                access_key_id=credentials["access_key_id"],
                secret_access_key=credentials["secret_access_key"],
            ),
            node_pools=[self._create_node_pool(p) for p in payload["node_pools"]],
            storage=self._create_aws_storage(payload["storage"]),
        )

    def _create_node_pool(self, payload: dict[str, Any]) -> NodePool:
        return NodePool(
            name=payload["name"],
            role=NodeRole(payload["role"]),
            min_size=payload["min_size"],
            max_size=payload["max_size"],
            cpu=payload["cpu"],
            available_cpu=payload["available_cpu"],
            memory_mb=payload["memory_mb"],
            available_memory_mb=payload["available_memory_mb"],
            disk_size_gb=payload.get("disk_size_gb", NodePool.disk_size_gb),
            disk_type=payload.get("disk_type", NodePool.disk_type),
            gpu=payload.get("gpu"),
            gpu_model=payload.get("gpu_model"),
            price=Decimal(payload.get("price", NodePool.price)),
            currency=payload.get("currency", NodePool.currency),
            machine_type=payload.get("machine_type"),
            idle_size=payload.get("idle_size", NodePool.idle_size),
            is_preemptible=payload.get("is_preemptible", NodePool.is_preemptible),
        )

    def _create_aws_storage(self, payload: dict[str, Any]) -> AWSStorage:
        result = AWSStorage(
            id=payload["id"],
            description=payload["description"],
            performance_mode=EFSPerformanceMode(payload["performance_mode"]),
            throughput_mode=EFSThroughputMode(payload["throughput_mode"]),
            instances=[self._create_storage_instance(p) for p in payload["instances"]],
        )
        return result

    def _create_google_cloud_provider(self, payload: dict[str, Any]) -> CloudProvider:
        return GoogleCloudProvider(
            location_type=ClusterLocationType(payload["location_type"]),
            region=payload["region"],
            zones=payload.get("zones", []),
            project=payload["project"],
            credentials=payload["credentials"],
            tpu_enabled=payload.get("tpu_enabled", False),
            node_pools=[self._create_node_pool(p) for p in payload["node_pools"]],
            storage=self._create_google_storage(payload["storage"]),
        )

    def _create_google_storage(self, payload: dict[str, Any]) -> GoogleStorage:
        result = GoogleStorage(
            id=payload["id"],
            description=payload["description"],
            backend=GoogleStorageBackend(payload["backend"]),
            tier=GoogleFilestoreTier(payload["tier"]) if "tier" in payload else None,
            instances=[self._create_storage_instance(p) for p in payload["instances"]],
        )
        return result

    def _create_azure_cloud_provider(self, payload: dict[str, Any]) -> CloudProvider:
        credentials = payload["credentials"]
        return AzureCloudProvider(
            region=payload["region"],
            resource_group=payload["resource_group"],
            virtual_network_cidr=payload.get("virtual_network_cidr", ""),
            credentials=AzureCredentials(
                subscription_id=credentials["subscription_id"],
                tenant_id=credentials["tenant_id"],
                client_id=credentials["client_id"],
                client_secret=credentials["client_secret"],
            ),
            node_pools=[self._create_node_pool(p) for p in payload["node_pools"]],
            storage=self._create_azure_storage(payload["storage"]),
        )

    def _create_azure_storage(self, payload: dict[str, Any]) -> AzureStorage:
        result = AzureStorage(
            id=payload["id"],
            description=payload["description"],
            replication_type=AzureReplicationType(payload["replication_type"]),
            tier=AzureStorageTier(payload["tier"]),
            instances=[self._create_storage_instance(p) for p in payload["instances"]],
        )
        return result

    def _create_on_prem_cloud_provider(self, payload: dict[str, Any]) -> CloudProvider:
        credentials = None
        if "credentials" in payload:
            if "token" in payload["credentials"]:
                credentials = KubernetesCredentials(
                    ca_data=payload["credentials"]["ca_data"],
                    token=payload["credentials"]["token"],
                )
            if "client_key_data" in payload["credentials"]:
                credentials = KubernetesCredentials(
                    ca_data=payload["credentials"]["ca_data"],
                    client_key_data=payload["credentials"]["client_key_data"],
                    client_cert_data=payload["credentials"]["client_cert_data"],
                )
        return OnPremCloudProvider(
            kubernetes_url=(
                URL(payload["kubernetes_url"]) if "kubernetes_url" in payload else None
            ),
            credentials=credentials,
            node_pools=[self._create_node_pool(p) for p in payload["node_pools"]],
            storage=None,
        )

    def _create_vcd_cloud_provider(self, payload: dict[str, Any]) -> CloudProvider:
        cp_type = CloudProviderType(payload["type"])
        credentials = payload["credentials"]
        organization = payload["organization"]
        virtual_data_center = payload["virtual_data_center"]
        return VCDCloudProvider(
            _type=cp_type,
            url=URL(payload["url"]),
            organization=organization,
            virtual_data_center=virtual_data_center,
            edge_name=payload["edge_name"],
            edge_external_network_name=payload["edge_external_network_name"],
            edge_public_ip=payload["edge_public_ip"],
            catalog_name=payload["catalog_name"],
            credentials=VCDCredentials(
                user=credentials["user"],
                password=credentials["password"],
                ssh_password=credentials.get("ssh_password"),
            ),
            node_pools=[self._create_node_pool(p) for p in payload["node_pools"]],
            storage=self._create_vcd_storage(payload["storage"]),
        )

    def _create_vcd_storage(self, payload: dict[str, Any]) -> VCDStorage:
        result = VCDStorage(
            description=payload["description"],
            profile_name=payload["profile_name"],
            size_gib=payload["size_gib"],
            instances=[self._create_storage_instance(p) for p in payload["instances"]],
        )
        return result

    def _create_storage_instance(self, payload: dict[str, Any]) -> StorageInstance:
        return StorageInstance(
            name=payload.get("name"),
            size_mb=payload.get("size_mb"),
            ready=payload["ready"],
        )

    @classmethod
    def create_credentials(
        cls, payload: dict[str, Any] | None
    ) -> CredentialsConfig | None:
        if not payload:
            return None
        grafana = payload.get("grafana")
        sentry = payload.get("sentry")
        docker_hub = payload.get("docker_hub")
        minio = payload.get("minio")
        emc_ecs = payload.get("emc_ecs")
        open_stack = payload.get("open_stack")
        return CredentialsConfig(
            neuro=cls._create_neuro_auth(payload["neuro"]),
            neuro_registry=cls._create_docker_registry(payload["neuro_registry"]),
            neuro_helm=cls._create_helm_registry(payload["neuro_helm"]),
            grafana=cls._create_grafana_credentials(grafana) if grafana else None,
            sentry=cls._create_sentry_credentials(sentry) if sentry else None,
            docker_hub=cls._create_docker_registry(docker_hub) if docker_hub else None,
            minio=cls._create_minio_credentials(minio) if minio else None,
            emc_ecs=cls._create_emc_ecs_credentials(emc_ecs) if emc_ecs else None,
            open_stack=cls._create_open_stack_credentials(open_stack)
            if open_stack
            else None,
        )

    @classmethod
    def _create_docker_registry(cls, payload: dict[str, Any]) -> DockerRegistryConfig:
        return DockerRegistryConfig(
            url=URL(payload["url"]),
            username=payload["username"],
            password=payload["password"],
            email=payload["email"],
        )

    @classmethod
    def _create_helm_registry(cls, payload: dict[str, Any]) -> HelmRegistryConfig:
        return HelmRegistryConfig(
            url=URL(payload["url"]),
            username=payload["username"],
            password=payload["password"],
        )

    @classmethod
    def _create_neuro_auth(cls, payload: dict[str, Any]) -> NeuroAuthConfig:
        return NeuroAuthConfig(
            url=URL(payload["url"]),
            token=payload["token"],
        )

    @classmethod
    def _create_grafana_credentials(cls, payload: dict[str, Any]) -> GrafanaCredentials:
        return GrafanaCredentials(
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


class PayloadFactory:
    @classmethod
    def create_credentials(cls, credentials: CredentialsConfig) -> dict[str, Any]:
        result = {
            "neuro": cls._create_neuro_auth(credentials.neuro),
            "neuro_helm": cls._create_helm_registry(credentials.neuro_helm),
            "neuro_registry": cls._create_docker_registry(credentials.neuro_registry),
        }
        if credentials.grafana is not None:
            result["grafana"] = cls._create_grafana_credentials(credentials.grafana)
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
        result: dict[str, Any] = {}
        if volume.path:
            result["path"] = volume.path
        if volume.size_mb is not None:
            result["size_mb"] = volume.size_mb
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
            "allow_privileged_mode": orchestrator.allow_privileged_mode,
        }
        if orchestrator.resource_pool_types:
            result["resource_pool_types"] = [
                self.create_resource_pool_type(r)
                for r in orchestrator.resource_pool_types
            ]
        if orchestrator.job_internal_hostname_template:
            result[
                "job_internal_hostname_template"
            ] = orchestrator.job_internal_hostname_template
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
            "memory_mb": resource_pool_type.memory_mb,
            "available_memory_mb": resource_pool_type.available_memory_mb,
            "disk_size_gb": resource_pool_type.disk_size_gb,
        }
        if resource_pool_type.gpu:
            result["gpu"] = resource_pool_type.gpu
            result["gpu_model"] = resource_pool_type.gpu_model
        if resource_pool_type.currency:
            result["price"] = str(resource_pool_type.price)
            result["currency"] = resource_pool_type.currency
        if resource_pool_type.tpu:
            result["tpu"] = cls.create_tpu_resource(resource_pool_type.tpu)
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
            "memory_mb": preset.memory_mb,
        }
        if preset.gpu:
            result["gpu"] = preset.gpu
            result["gpu_model"] = preset.gpu_model
        if preset.tpu:
            result["tpu"] = cls._create_tpu_preset(preset.tpu)
        if preset.scheduler_enabled:
            result["scheduler_enabled"] = preset.scheduler_enabled
        if preset.preemptible_node:
            result["preemptible_node"] = preset.preemptible_node
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
        if idle_job.image_pull_secret:
            result["image_pull_secret"] = idle_job.image_pull_secret
        if idle_job.env:
            result["env"] = idle_job.env
        if idle_job.node_selector:
            result["node_selector"] = idle_job.node_selector
        return result

    @classmethod
    def _create_resources(cls, resources: Resources) -> dict[str, Any]:
        result = {"cpu_m": resources.cpu_m, "memory_mb": resources.memory_mb}
        if resources.gpu:
            result["gpu"] = resources.gpu
        return result

    @classmethod
    def create_monitoring(cls, monitoring: MonitoringConfig) -> dict[str, Any]:
        return {"url": str(monitoring.url)}

    @classmethod
    def create_metrics(cls, metrics: MetricsConfig) -> dict[str, Any]:
        return {"url": str(metrics.url)}

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
            "storage_limit_per_user_gb": disks.storage_limit_per_user_gb,
        }

    @classmethod
    def create_ingress(cls, ingress: IngressConfig) -> dict[str, Any]:
        result: dict[str, Any] = {"acme_environment": ingress.acme_environment.value}
        if ingress.cors_origins:
            result["cors_origins"] = ingress.cors_origins
        return result
