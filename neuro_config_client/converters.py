from decimal import Decimal
from typing import Any

from yarl import URL

from .models import (
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
    CloudProvider,
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
    NodeRole,
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


class PrimitiveToClusterConverter:
    def convert_cluster(self, payload: dict[str, Any]) -> Cluster:
        orchestrator = None
        if payload.get("orchestrator"):
            orchestrator = self.convert_orchestrator(payload["orchestrator"])
        storage = None
        if payload.get("storage"):
            storage = self.convert_storage(payload["storage"])
        blob_storage = None
        if payload.get("blob_storage"):
            blob_storage = self.convert_blob_storage(payload["blob_storage"])
        registry = None
        if payload.get("registry"):
            registry = self.convert_registry(payload["registry"])
        monitoring = None
        if payload.get("monitoring"):
            monitoring = self.convert_monitoring(payload["monitoring"])
        secrets = None
        if payload.get("secrets"):
            secrets = self.convert_secrets(payload["secrets"])
        metrics = None
        if payload.get("metrics"):
            metrics = self.convert_metrics(payload["metrics"])
        disks = None
        if payload.get("disks"):
            disks = self.convert_disks(payload["disks"])
        buckets = None
        if payload.get("buckets"):
            buckets = self.convert_buckets(payload["buckets"])
        ingress = None
        if payload.get("ingress"):
            ingress = self.convert_ingress(payload["ingress"])
        dns = None
        if payload.get("dns"):
            dns = self.convert_dns(payload["dns"])
        cloud_provider = None
        if payload.get("cloud_provider"):
            cloud_provider = self.convert_cloud_provider(payload["cloud_provider"])
        return Cluster(
            name=payload["name"],
            orchestrator=orchestrator,
            storage=storage,
            blob_storage=blob_storage,
            registry=registry,
            monitoring=monitoring,
            secrets=secrets,
            metrics=metrics,
            disks=disks,
            buckets=buckets,
            ingress=ingress,
            dns=dns,
            cloud_provider=cloud_provider,
        )

    def convert_orchestrator(self, payload: dict[str, Any]) -> OrchestratorConfig:
        return OrchestratorConfig(
            job_hostname_template=payload["job_hostname_template"],
            job_internal_hostname_template=payload.get(
                "job_internal_hostname_template", ""
            ),
            job_fallback_hostname=payload["job_fallback_hostname"],
            job_schedule_timeout_s=payload["job_schedule_timeout_s"],
            job_schedule_scale_up_timeout_s=payload["job_schedule_scale_up_timeout_s"],
            is_http_ingress_secure=payload["is_http_ingress_secure"],
            resource_pool_types=[
                self.convert_resource_pool_type(r)
                for r in payload.get("resource_pool_types", [])
            ],
            resource_presets=[
                self.convert_resource_preset(preset)
                for preset in payload.get("resource_presets", [])
            ],
            allow_privileged_mode=payload["allow_privileged_mode"],
            pre_pull_images=payload.get("pre_pull_images", ()),
            idle_jobs=[
                self.convert_idle_job(job) for job in payload.get("idle_jobs", ())
            ],
        )

    def convert_resource_pool_type(self, payload: dict[str, Any]) -> ResourcePoolType:
        tpu = None
        if payload.get("tpu"):
            tpu = self.convert_tpu_resource(payload["tpu"])
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

    def convert_tpu_resource(self, payload: dict[str, Any]) -> TPUResource:
        return TPUResource(
            ipv4_cidr_block=payload["ipv4_cidr_block"],
            types=list(payload["types"]),
            software_versions=list(payload["software_versions"]),
        )

    def convert_resource_preset(self, payload: dict[str, Any]) -> ResourcePreset:
        tpu = None
        if payload.get("tpu"):
            tpu = self.convert_tpu_preset(payload["tpu"])
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

    def convert_tpu_preset(self, payload: dict[str, Any]) -> TPUPreset:
        return TPUPreset(
            type=payload["type"], software_version=payload["software_version"]
        )

    def convert_idle_job(self, payload: dict[str, Any]) -> IdleJobConfig:
        return IdleJobConfig(
            count=payload["count"],
            image=payload["image"],
            image_secret=payload.get("image_secret", ""),
            resources=self.convert_resources(payload["resources"]),
            env=payload.get("env") or {},
            node_selector=payload.get("node_selector") or {},
        )

    def convert_resources(self, payload: dict[str, Any]) -> Resources:
        return Resources(
            cpu_m=payload["cpu_m"],
            memory_mb=payload["memory_mb"],
            gpu=payload.get("gpu", 0),
        )

    def convert_storage(self, payload: dict[str, Any]) -> StorageConfig:
        return StorageConfig(
            url=URL(payload["url"]),
            volumes=[self.convert_volume(e) for e in payload.get("volumes", ())],
        )

    def convert_volume(self, payload: dict[str, Any]) -> VolumeConfig:
        return VolumeConfig(path=payload.get("path"), size_mb=payload.get("size_mb"))

    def convert_blob_storage(self, payload: dict[str, Any]) -> BlobStorageConfig:
        return BlobStorageConfig(url=URL(payload["url"]))

    def convert_registry(self, payload: dict[str, Any]) -> RegistryConfig:
        return RegistryConfig(url=URL(payload["url"]))

    def convert_monitoring(self, payload: dict[str, Any]) -> MonitoringConfig:
        return MonitoringConfig(url=URL(payload["url"]))

    def convert_secrets(self, payload: dict[str, Any]) -> SecretsConfig:
        return SecretsConfig(url=URL(payload["url"]))

    def convert_metrics(self, payload: dict[str, Any]) -> MetricsConfig:
        return MetricsConfig(url=URL(payload["url"]))

    def convert_dns(self, payload: dict[str, Any]) -> DNSConfig:
        return DNSConfig(
            name=payload["name"],
            a_records=[self.convert_a_record(r) for r in payload.get("a_records", [])],
        )

    def convert_a_record(self, payload: dict[str, Any]) -> ARecord:
        return ARecord(
            name=payload["name"],
            ips=payload.get("ips", []),
            dns_name=payload.get("dns_name", ARecord.dns_name),
            zone_id=payload.get("zone_id", ARecord.zone_id),
            evaluate_target_health=payload.get(
                "evaluate_target_health", ARecord.evaluate_target_health
            ),
        )

    def convert_disks(self, payload: dict[str, Any]) -> DisksConfig:
        return DisksConfig(
            url=URL(payload["url"]),
            storage_limit_per_user_gb=payload["storage_limit_per_user_gb"],
        )

    def convert_buckets(self, payload: dict[str, Any]) -> BucketsConfig:
        return BucketsConfig(
            url=URL(payload["url"]),
            disable_creation=payload.get("disable_creation", False),
        )

    def convert_ingress(self, payload: dict[str, Any]) -> IngressConfig:
        return IngressConfig(
            acme_environment=ACMEEnvironment(payload["acme_environment"]),
            cors_origins=payload.get("cors_origins", ()),
        )

    def convert_cloud_provider(self, payload: dict[str, Any]) -> CloudProvider:
        cp_type = CloudProviderType(payload["type"].lower())
        if cp_type == CloudProviderType.AWS:
            return self._convert_aws_cloud_provider(payload)
        elif cp_type == CloudProviderType.GCP:
            return self._convert_google_cloud_provider(payload)
        elif cp_type == CloudProviderType.AZURE:
            return self._convert_azure_cloud_provider(payload)
        elif cp_type == CloudProviderType.ON_PREM:
            return self._convert_on_prem_cloud_provider(payload)
        elif cp_type.startswith("vcd_"):
            return self._convert_vcd_cloud_provider(payload)
        raise ValueError(f"Cloud provider '{cp_type}' is not supported")

    def _convert_aws_cloud_provider(self, payload: dict[str, Any]) -> CloudProvider:
        credentials = payload["credentials"]
        return AWSCloudProvider(
            region=payload["region"],
            zones=payload["zones"],
            vpc_id=payload.get("vpc_id"),
            credentials=AWSCredentials(
                access_key_id=credentials["access_key_id"],
                secret_access_key=credentials["secret_access_key"],
            ),
            node_pools=[self._convert_node_pool(p) for p in payload["node_pools"]],
            storage=self._convert_aws_storage(payload["storage"]),
        )

    def _convert_node_pool(self, payload: dict[str, Any]) -> NodePool:
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

    def _convert_aws_storage(self, payload: dict[str, Any]) -> AWSStorage:
        result = AWSStorage(
            id=payload["id"],
            description=payload["description"],
            performance_mode=EFSPerformanceMode(payload["performance_mode"]),
            throughput_mode=EFSThroughputMode(payload["throughput_mode"]),
            instances=[self._convert_storage_instance(p) for p in payload["instances"]],
        )
        return result

    def _convert_google_cloud_provider(self, payload: dict[str, Any]) -> CloudProvider:
        return GoogleCloudProvider(
            location_type=ClusterLocationType(payload["location_type"]),
            region=payload["region"],
            zones=payload.get("zones", []),
            project=payload["project"],
            credentials=payload["credentials"],
            tpu_enabled=payload.get("tpu_enabled", False),
            node_pools=[self._convert_node_pool(p) for p in payload["node_pools"]],
            storage=self._convert_google_storage(payload["storage"]),
        )

    def _convert_google_storage(self, payload: dict[str, Any]) -> GoogleStorage:
        result = GoogleStorage(
            id=payload["id"],
            description=payload["description"],
            backend=GoogleStorageBackend(payload["backend"]),
            tier=GoogleFilestoreTier(payload["tier"]) if "tier" in payload else None,
            instances=[self._convert_storage_instance(p) for p in payload["instances"]],
        )
        return result

    def _convert_azure_cloud_provider(self, payload: dict[str, Any]) -> CloudProvider:
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
            node_pools=[self._convert_node_pool(p) for p in payload["node_pools"]],
            storage=self._convert_azure_storage(payload["storage"]),
        )

    def _convert_azure_storage(self, payload: dict[str, Any]) -> AzureStorage:
        result = AzureStorage(
            id=payload["id"],
            description=payload["description"],
            replication_type=AzureReplicationType(payload["replication_type"]),
            tier=AzureStorageTier(payload["tier"]),
            instances=[self._convert_storage_instance(p) for p in payload["instances"]],
        )
        return result

    def _convert_on_prem_cloud_provider(self, payload: dict[str, Any]) -> CloudProvider:
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
            node_pools=[self._convert_node_pool(p) for p in payload["node_pools"]],
            storage=None,
        )

    def _convert_vcd_cloud_provider(self, payload: dict[str, Any]) -> CloudProvider:
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
            node_pools=[self._convert_node_pool(p) for p in payload["node_pools"]],
            storage=self._convert_vcd_storage(payload["storage"]),
        )

    def _convert_vcd_storage(self, payload: dict[str, Any]) -> VCDStorage:
        result = VCDStorage(
            description=payload["description"],
            profile_name=payload["profile_name"],
            size_gib=payload["size_gib"],
            instances=[self._convert_storage_instance(p) for p in payload["instances"]],
        )
        return result

    def _convert_storage_instance(self, payload: dict[str, Any]) -> StorageInstance:
        return StorageInstance(
            name=payload.get("name"),
            size_mb=payload.get("size_mb"),
            ready=payload["ready"],
        )
