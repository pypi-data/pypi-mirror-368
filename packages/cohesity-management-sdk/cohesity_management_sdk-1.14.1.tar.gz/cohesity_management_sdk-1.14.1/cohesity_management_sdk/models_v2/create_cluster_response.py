# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.cluster_network_config_3
import cohesity_management_sdk.models_v2.views_global_settings
import cohesity_management_sdk.models_v2.supported_config
import cohesity_management_sdk.models_v2.cluster_stats
import cohesity_management_sdk.models_v2.schema_info
import cohesity_management_sdk.models_v2.rigel_cluster_params
import cohesity_management_sdk.models_v2.cluster_proxy_server_config
import cohesity_management_sdk.models_v2.ntp_settings
import cohesity_management_sdk.models_v2.load_balancer_config
import cohesity_management_sdk.models_v2.license_state
import cohesity_management_sdk.models_v2.cluster_hardware_info
import cohesity_management_sdk.models_v2.audit_log_config
import cohesity_management_sdk.models_v2.eula_config
import cohesity_management_sdk.models_v2.disk_count_by_tier
import cohesity_management_sdk.models_v2.cluster_audit_log_config
import cohesity_management_sdk.models_v2.cluster_amqp_target_config
import cohesity_management_sdk.models_v2.subnet_5
import cohesity_management_sdk.models_v2.node_specific_response

class CreateClusterResponse(object):

    """Implementation of the 'Create Cluster Response.' model.

    Specifies the cluster details.

    Attributes:
        aes_encryption_mode (string): Specifies the default AES Encryption mode on the cluster.
        amqp_target_config (ClusterAMQPTargetConfig): Specifies the AMQP target config.
        apps_subnet (Subnet5): The subnet for Athena apps.
        assigned_racks_count (long|int): Specifies the number of racks in cluster with at least one rack
          assigned.
        attempt_agent_ports_upgrade (bool): To attempt agent connection on port 21213 first.
        auth_support_for_pkg_downloads (bool): Specifies if cluster can support authHeaders for upgrade.
        auth_type (AuthType1Enum): Specifies the authentication scheme for the cluster.
        authorized_ssh_public_keys (list of string): Specifies a list of authorized SSH public keys that have been
          uploaded to this Cohesity Cluster.
        available_metadata_space (long|int): Specifies information about storage available for metadata
        banner_enabled (bool): Specifies whether UI banner is enabled on the cluster or not.
        chassis_count (long|int): Specifies the number of chassis in cluster.
        cluster_audit_log_config (ClusterAuditLogConfig): TODO: type description here.
        cluster_size (ClusterSizeEnum): Specifies the size of the cloud platforms.
        cluster_software_version (string): Specifies the current release of the Cohesity software running
          on the Cohesity Cluster.
        cluster_type (ClusterTypeEnum): Specifies the environment type of the cluster.
        created_time_msecs (long|int): Specifies the time when the Cohesity Cluster was created.
        current_op_scheduled_time_secs (long|int): Specifies the time scheduled by the Cohesity Cluster to start
          the current running operation.
        current_operation (CurrentOperationEnum): Specifies the current Cluster-level operation in progress.
        current_time_msecs (long|int): Specifies the current system time on the Cohesity Cluster.
        description (string): Description of the cluster.
        disk_count_by_tier (list of DiskCountByTier): Specifies the number of disks on the cluster by Storage Tier.
        dns_server_ips (list of string): Specifies the IP addresses of the DNS Servers used by the Cohesity
          Cluster.
        domain_names (list of string): Specifies array of Domain Names.
        enable_active_monitoring (bool): Specifies if Cohesity can receive monitoring information from
          the Cohesity Cluster.
        enable_encryption (bool): Specifies whether or not encryption is enabled. If encryption
          is enabled, all data on the Cluster will be encrypted.
        enable_patches_download (bool): Specifies whether to enable downloading patches from Cohesity
          download site.
        enable_upgrade_pkg_polling (bool): If 'true', Cohesity's upgrade server is polled for new releases.
        encryption_key_rotation_period_secs (long|int): Specifies the period of time (in seconds) when encryption keys
          are rotated
        eula_config (EulaConfig): Specifies the End User License Agreement acceptance information.
        fault_tolerance_level (FaultToleranceLevelEnum): Specifies the level which 'MetadataFaultToleranceFactor' applies
          to.
        file_services_audit_log_config (): Specifies the File Services audit log configuration.
        gateway (string): Specifies the gateway IP address.
        google_analytics_enabled (bool): Specifies whether Google Analytics is enabled.
        hardware_encryption_enabled (bool): Specifies if hardware encryption(SED) is enabled.
        hardware_info (ClusterHardwareInfo): Specifies a hardware type for motherboard of the nodes that make
          dnsServerIps this Cohesity Cluster
        id (long|int): Specifies the cluster id of the cluster.
        incarnation_id (long|int): Specifies the incarnation id of the cluster.
        ip_preference (long|int): Specifies IP preference.
        is_athena_subnet_clash (bool): Specifies whether or not athena subnet is clashing with some
          other internal subnet
        is_cluster_mfa_enabled (bool): Specifies if MFA is enabled on cluster.
        is_documentation_local (bool): Specifies what version of the documentation is used.
        is_patch_apply_aborted (bool): Specifies that the patch apply was aborted.
        is_patch_revert_aborted (bool): Specifies that the patch revert was aborted.
        is_upgrade_aborted (bool): Specifies if the current upgrade has been aborted.
        kms_server_id (long|int): Specifies the KMS Server Id.
        language_locale (string): Specifies the language and locale for this Cohesity Cluster.
        license_state (): Specifies the state of licensing workflow.
        load_balancer_vip_config (LoadBalancerConfig): Load balancer VIP config for OneHelios cluster.
        local_auth_domain_name (string): Specifies domain name for SMB local authentication.
        local_groups_enabled (bool): Specifies whether to enable local groups on cluster.
        local_tenant_id (string): Specifies the local tenant id. Only applicable on Helios.
        metadata_fault_tolerance_factor (long|int): Specifies metadata fault tolerance setting for the cluster.
        minimum_failure_domains_needed (long|int): Specifies minimum failure domains needed in the cluster.
        multi_tenancy_enabled (bool): Specifies if multi tenancy is enabled in the cluster.
        name (string): Name of the cluster.
        network_config (ClusterNetworkConfig): Network config of the cluster.
        node_count (long|int): Specifies the number of Nodes in the Cohesity Cluster.
        node_ips (string): Specifies IP addresses of nodes in the cluster.
        ntp_settings (NTPSettings): Specifies if the ntp/primary secondary scheme should be disabled
        patch_apply_failure_error_message (string): Specifies the error message for a failed patch apply.
        patch_revert_failure_error_message (string): Specifies the error message for a failed patch revert.
        patch_revert_version (string): Specifies the target version for reverting the patch.
        patch_target_version (string): Specifies the target version for applying the patch.
        patch_v2_reverts_allowed (bool): Specifies if cluster can support patch reverts.
        patch_version (string): Specifies the patch version applied to cluster.
        pcie_ssd_tier_rebalance_delay_secs (long_int): Specifies the rebalance delay in seconds for cluster PcieSSD
          storage tier.
        proto_rpc_encryption_enabled (bool): Specifies if protorpc encryption is enabled or not.
        proxy_server_config (ClusterProxyServerConfig): Specifies the proxy to use for external HTTP traffic.
        proxy_v_m_subnet (string): Specifies the subnet reserved for ProxyVM.
        region_id (string): Specifies the region id on which this cluster is present. Only
          applicable on Helios for DMaaS clusters.
        reverse_tunnel_enabled (bool): If 'true', Cohesity's Remote Tunnel is enabled.
        reverse_tunnel_end_time_msecs (long|int): Specifies the end time in milliseconds since epoch until when
          the reverse tunnel will stay enabled.
        rigel_cluster_params (RigelClusterParams): Specifies the Rigel specific parameters.
        s3_virtual_hosted_domain_names (list of string): Specifies the list of domain names for S3.
        sata_hdd_tier_admission_control (long|int): Specifies the admission control for cluster SATAHDD storage tier.
        schema_info_list (list of SchemaInfo): Specifies the time series schema info of the cluster.
        security_mode_dod (bool): Specifies if Security Mode DOD is enabled or not.
        smb_ad_disabled (bool): Specifies if Active Directory should be disabled for authentication
          of SMB shares.
        smb_multichannel_enabled (bool): Specifies whether SMB multichannel is enabled on the cluster.
        software_type (SoftwareTypeEnum):  Specifies the type of Cohesity Software.
        split_key_host_access (bool): Specifies if split key host access is enabled.
        stats (ClusterStats): Specifies statistics about the Cohesity Cluster.
        supported_config (SupportedConfig): Specifies information about supported configuration.
        sw_version (string): Software version of the cluster.
        target_software_version (string): Specifies the Cohesity release that this Cluster is being upgraded
          to if an upgrade operation is in progress.
        tenant_id (string): Specifies the globally unique tenant id. Only applicable on Helios.
        tenant_viewbox_sharing_enabled (bool): Specifies whether multiple tenants can be placed on the same
          viewbox.
        timezone (string): Specifies the timezone to use.
        trust_domain (string): Specifies the Trust Domain.
        turbo_mode (bool): Specifies if the cluster is in Turbo mode..
        type (Type74Enum): Specifies the type of the cluster.
        upgrade_failure_error_string (string): Error string to capture why the upgrade failed.
        use_default_agent_ports (bool): To use default ports 50051 & 21213.
        use_heimdall (bool): Specifies whether to enable Heimdall which tells whether services
          should use temporary fleet instances to mount disks by talking to Heimdall.
        used_metadata_space_pct (long|int): Measures the percentage about storage used for metadata over
          the total storage available for metadata
        views_global_settings (ViewsGlobalSettings): Specifies the Global Settings for SmartFiles.
        message (string): Specifies an optional message field
        healthy_nodes (list of NodeSpecificResponse): List of healthy nodes in
            cluster.
        unhealthy_nodes (list of NodeSpecificResponse): List of unhealthy
            nodes in cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "aes_encryption_mode":'aesEncryptionMode',
        "amqp_target_config":'amqpTargetConfig',
        "apps_subnet":'appsSubnet',
        "assigned_racks_count":'assignedRacksCount',
        "attempt_agent_ports_upgrade":'attemptAgentPortsUpgrade',
        "auth_support_for_pkg_downloads":'authSupportForPkgDownloads',
        "auth_type":'authType',
        "authorized_ssh_public_keys":'authorizedSshPublicKeys',
        "available_metadata_space":'availableMetadataSpace',
        "banner_enabled":'bannerEnabled',
        "chassis_count":'chassisCount',
        "cluster_audit_log_config":'clusterAuditLogConfig',
        "cluster_size":'clusterSize',
        "cluster_software_version":'clusterSoftwareVersion',
        "cluster_type":'clusterType',
        "created_time_msecs":'createdTimeMsecs',
        "current_op_scheduled_time_secs":'currentOpScheduledTimeSecs',
        "current_operation":'currentOperation',
        "current_time_msecs":'currentTimeMsecs',
        "description":'description',
        "disk_count_by_tier":'diskCountByTier',
        "dns_server_ips":'dnsServerIps',
        "domain_names":'domainNames',
        "enable_active_monitoring":'enableActiveMonitoring',
        "enable_encryption":'enableEncryption',
        "enable_patches_download":'enablePatchesDownload',
        "enable_upgrade_pkg_polling":'enableUpgradePkgPolling',
        "encryption_key_rotation_period_secs":'encryptionKeyRotationPeriodSecs',
        "eula_config":'eulaConfig',
        "fault_tolerance_level":'faultToleranceLevel',
        "file_services_audit_log_config":'fileServicesAuditLogConfig',
        "gateway":'gateway',
        "google_analytics_enabled":'googleAnalyticsEnabled',
        "hardware_encryption_enabled":'hardwareEncryptionEnabled',
        "hardware_info":'hardwareInfo',
        "id":'id',
        "incarnation_id":'incarnationId',
        "ip_preference":'ipPreference',
        "is_athena_subnet_clash":'isAthenaSubnetClash',
        "is_cluster_mfa_enabled":'isClusterMfaEnabled',
        "is_documentation_local":'isDocumentationLocal',
        "is_patch_apply_aborted":'isPatchApplyAborted',
        "is_patch_revert_aborted":'isPatchRevertAborted',
        "is_upgrade_aborted":'isUpgradeAborted',
        "kms_server_id":'kmsServerId',
        "language_locale":'languageLocale',
        "license_state":'licenseState',
        "load_balancer_vip_config":'loadBalancerVipConfig',
        "local_auth_domain_name":'localAuthDomainName',
        "local_groups_enabled":'localGroupsEnabled',
        "local_tenant_id":'localTenantId',
        "metadata_fault_tolerance_factor":'metadataFaultToleranceFactor',
        "minimum_failure_domains_needed":'minimumFailureDomainsNeeded',
        "multi_tenancy_enabled":'multiTenancyEnabled',
        "name":'name',
        "network_config":'networkConfig',
        "node_count":'nodeCount',
        "node_ips":'nodeIps',
        "ntp_settings":'ntpSettings',
        "patch_apply_failure_error_message":'patchApplyFailureErrorMessage',
        "patch_revert_failure_error_message":'patchRevertFailureErrorMessage',
        "patch_revert_version":'patchRevertVersion',
        "patch_target_version":'patchTargetVersion',
        "patch_v2_reverts_allowed":'patchV2RevertsAllowed',
        "patch_version":'patchVersion',
        "pcie_ssd_tier_rebalance_delay_secs":'pcieSsdTierRebalanceDelaySecs',
        "proto_rpc_encryption_enabled":'protoRpcEncryptionEnabled',
        "proxy_server_config":"proxyServerConfig",
        "proxy_v_m_subnet":'proxyVMSubnet',
        "region_id":'regionId',
        "reverse_tunnel_enabled":'reverseTunnelEnabled',
        "reverse_tunnel_end_time_msecs":'reverseTunnelEndTimeMsecs',
        "rigel_cluster_params":'rigelClusterParams',
        "s3_virtual_hosted_domain_names":'s3VirtualHostedDomainNames',
        "sata_hdd_tier_admission_control":'sataHddTierAdmissionControl',
        "schema_info_list":'schemaInfoList',
        "security_mode_dod":'securityModeDod',
        "smb_ad_disabled":'smbAdDisabled',
        "smb_multichannel_enabled":'smbMultichannelEnabled',
        "software_type":'softwareType',
        "split_key_host_access":'splitKeyHostAccess',
        "stats":'stats',
        "supported_config":'supportedConfig',
        "sw_version":'swVersion',
        "target_software_version":'targetSoftwareVersion',
        "tenant_id":'tenantId',
        "tenant_viewbox_sharing_enabled":'tenantViewboxSharingEnabled',
        "timezone":'timezone',
        "trust_domain":'trustDomain',
        "turbo_mode":'turboMode',
        "mtype":'type',
        "upgrade_failure_error_string":'upgradeFailureErrorString',
        "use_default_agent_ports":'useDefaultAgentPorts',
        "use_heimdall":'useHeimdall',
        "used_metadata_space_pct":'usedMetadataSpacePct',
        "views_global_settings":'viewsGlobalSettings',
        "message":'message',
        "healthy_nodes":'healthyNodes',
        "unhealthy_nodes":'unhealthyNodes'
    }

    def __init__(self,
                 aes_encryption_mode=None ,
                 amqp_target_config=None ,
                 apps_subnet=None ,
                 assigned_racks_count=None ,
                 attempt_agent_ports_upgrade=None ,
                 auth_support_for_pkg_downloads=None ,
                 auth_type=None ,
                 authorized_ssh_public_keys=None ,
                 available_metadata_space=None ,
                 banner_enabled=None ,
                 chassis_count=None ,
                 cluster_audit_log_config=None ,
                 cluster_size=None ,
                 cluster_software_version=None ,
                 cluster_type=None ,
                 created_time_msecs=None ,
                 current_op_scheduled_time_secs=None ,
                 current_operation=None ,
                 current_time_msecs=None ,
                 description=None ,
                 disk_count_by_tier=None ,
                 dns_server_ips=None ,
                 domain_names=None ,
                 enable_active_monitoring=None ,
                 enable_encryption=None ,
                 enable_patches_download=None ,
                 enable_upgrade_pkg_polling=None ,
                 encryption_key_rotation_period_secs=None ,
                 eula_config=None ,
                 fault_tolerance_level=None ,
                 file_services_audit_log_config=None ,
                 gateway=None ,
                 google_analytics_enabled=None ,
                 hardware_encryption_enabled=None ,
                 hardware_info=None ,
                 id=None ,
                 incarnation_id=None ,
                 ip_preference=None ,
                 is_athena_subnet_clash=None,
                 is_cluster_mfa_enabled=None,
                 is_documentation_local=None ,
                 is_patch_apply_aborted=None ,
                 is_patch_revert_aborted=None ,
                 is_upgrade_aborted=None ,
                 kms_server_id=None ,
                 language_locale=None ,
                 license_state=None ,
                 load_balancer_vip_config=None ,
                 local_auth_domain_name=None ,
                 local_groups_enabled=None ,
                 local_tenant_id=None ,
                 metadata_fault_tolerance_factor=None ,
                 minimum_failure_domains_needed=None ,
                 multi_tenancy_enabled=None ,
                 name=None ,
                 network_config=None ,
                 node_count=None ,
                 node_ips=None ,
                 ntp_settings=None ,
                 patch_apply_failure_error_message=None ,
                 patch_revert_failure_error_message=None ,
                 patch_revert_version=None ,
                 patch_target_version=None ,
                 patch_v2_reverts_allowed=None ,
                 patch_version=None ,
                 pcie_ssd_tier_rebalance_delay_secs=None ,
                 proto_rpc_encryption_enabled=None ,
                 proxy_server_config=None ,
                 proxy_v_m_subnet=None ,
                 region_id=None ,
                 reverse_tunnel_enabled=None ,
                 reverse_tunnel_end_time_msecs=None ,
                 rigel_cluster_params=None ,
                 s3_virtual_hosted_domain_names=None ,
                 sata_hdd_tier_admission_control=None ,
                 schema_info_list=None ,
                 security_mode_dod=None ,
                 smb_ad_disabled=None ,
                 smb_multichannel_enabled=None ,
                 software_type=None ,
                 split_key_host_access=None ,
                 stats=None ,
                 supported_config=None ,
                 sw_version=None ,
                 target_software_version=None ,
                 tenant_id=None ,
                 tenant_viewbox_sharing_enabled=None ,
                 timezone=None ,
                 trust_domain=None ,
                 turbo_mode=None ,
                 mtype=None ,
                 upgrade_failure_error_string=None ,
                 use_default_agent_ports=None ,
                 use_heimdall=None ,
                 used_metadata_space_pct=None ,
                 views_global_settings=None,
                 message=None,
                 healthy_nodes=None,
                 unhealthy_nodes=None):
        """Constructor for the CreateClusterResponse class"""

        # Initialize members of the class
        self.aes_encryption_mode = aes_encryption_mode
        self.amqp_target_config = amqp_target_config
        self.apps_subnet = apps_subnet
        self.assigned_racks_count = assigned_racks_count
        self.attempt_agent_ports_upgrade = attempt_agent_ports_upgrade
        self.auth_support_for_pkg_downloads = auth_support_for_pkg_downloads
        self.auth_type = auth_type
        self.authorized_ssh_public_keys = authorized_ssh_public_keys
        self.available_metadata_space = available_metadata_space
        self.banner_enabled = banner_enabled
        self.chassis_count = chassis_count
        self.cluster_audit_log_config = cluster_audit_log_config
        self.cluster_size = cluster_size
        self.cluster_software_version = cluster_software_version
        self.cluster_type = cluster_type
        self.created_time_msecs = created_time_msecs
        self.current_op_scheduled_time_secs = current_op_scheduled_time_secs
        self.current_operation = current_operation
        self.current_time_msecs = current_time_msecs
        self.description = description
        self.disk_count_by_tier = disk_count_by_tier
        self.dns_server_ips = dns_server_ips
        self.domain_names = domain_names
        self.enable_active_monitoring = enable_active_monitoring
        self.enable_encryption = enable_encryption
        self.enable_patches_download = enable_patches_download
        self.enable_upgrade_pkg_polling = enable_upgrade_pkg_polling
        self.encryption_key_rotation_period_secs = encryption_key_rotation_period_secs
        self.eula_config = eula_config
        self.fault_tolerance_level = fault_tolerance_level
        self.file_services_audit_log_config = file_services_audit_log_config
        self.gateway = gateway
        self.google_analytics_enabled = google_analytics_enabled
        self.hardware_encryption_enabled = hardware_encryption_enabled
        self.hardware_info = hardware_info
        self.id = id
        self.incarnation_id = incarnation_id
        self.ip_preference = ip_preference
        self.is_athena_subnet_clash = is_athena_subnet_clash
        self.is_cluster_mfa_enabled = is_cluster_mfa_enabled
        self.is_documentation_local = is_documentation_local
        self.is_patch_apply_aborted = is_patch_apply_aborted
        self.is_patch_revert_aborted = is_patch_revert_aborted
        self.is_upgrade_aborted = is_upgrade_aborted
        self.kms_server_id = kms_server_id
        self.language_locale = language_locale
        self.license_state = license_state
        self.load_balancer_vip_config = load_balancer_vip_config
        self.local_auth_domain_name = local_auth_domain_name
        self.local_groups_enabled = local_groups_enabled
        self.local_tenant_id = local_tenant_id
        self.metadata_fault_tolerance_factor = metadata_fault_tolerance_factor
        self.minimum_failure_domains_needed = minimum_failure_domains_needed
        self.multi_tenancy_enabled = multi_tenancy_enabled
        self.name = name
        self.network_config = network_config
        self.node_count = node_count
        self.node_ips = node_ips
        self.ntp_settings = ntp_settings
        self.patch_apply_failure_error_message = patch_apply_failure_error_message
        self.patch_revert_failure_error_message = patch_revert_failure_error_message
        self.patch_revert_version = patch_revert_version
        self.patch_target_version = patch_target_version
        self.patch_v2_reverts_allowed = patch_v2_reverts_allowed
        self.patch_version = patch_version
        self.pcie_ssd_tier_rebalance_delay_secs = pcie_ssd_tier_rebalance_delay_secs
        self.proto_rpc_encryption_enabled = proto_rpc_encryption_enabled
        self.proxy_server_config = proxy_server_config
        self.proxy_v_m_subnet = proxy_v_m_subnet
        self.region_id = region_id
        self.reverse_tunnel_enabled = reverse_tunnel_enabled
        self.reverse_tunnel_end_time_msecs = reverse_tunnel_end_time_msecs
        self.rigel_cluster_params = rigel_cluster_params
        self.s3_virtual_hosted_domain_names = s3_virtual_hosted_domain_names
        self.sata_hdd_tier_admission_control = sata_hdd_tier_admission_control
        self.schema_info_list = schema_info_list
        self.security_mode_dod = security_mode_dod
        self.smb_ad_disabled = smb_ad_disabled
        self.smb_multichannel_enabled = smb_multichannel_enabled
        self.software_type = software_type
        self.split_key_host_access = split_key_host_access
        self.stats = stats
        self.supported_config = supported_config
        self.sw_version = sw_version
        self.target_software_version = target_software_version
        self.tenant_id = tenant_id
        self.tenant_viewbox_sharing_enabled = tenant_viewbox_sharing_enabled
        self.timezone = timezone
        self.trust_domain = trust_domain
        self.turbo_mode = turbo_mode
        self.mtype = mtype
        self.upgrade_failure_error_string = upgrade_failure_error_string
        self.use_default_agent_ports = use_default_agent_ports
        self.use_heimdall = use_heimdall
        self.used_metadata_space_pct = used_metadata_space_pct
        self.views_global_settings = views_global_settings
        self.message = message
        self.healthy_nodes = healthy_nodes
        self.unhealthy_nodes = unhealthy_nodes


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        aes_encryption_mode = dictionary.get('aesEncryptionMode')
        amqp_target_config = cohesity_management_sdk.models_v2.cluster_amqp_target_config.ClusterAMQPTargetConfig.from_dictionary(
            dictionary.get('amqpTargetConfig')) if dictionary.get('amqpTargetConfig') else None
        apps_subnet = cohesity_management_sdk.models_v2.subnet_5.Subnet5.from_dictionary(
            dictionary.get('appsSubnet')) if dictionary.get('appsSubnet') else None
        assigned_racks_count = dictionary.get('assignedRacksCount')
        attempt_agent_ports_upgrade = dictionary.get('attemptAgentPortsUpgrade')
        auth_support_for_pkg_downloads = dictionary.get('authSupportForPkgDownloads')
        auth_type = dictionary.get('authType')
        authorized_ssh_public_keys = dictionary.get('authorizedSshPublicKeys')
        available_metadata_space = dictionary.get('availableMetadataSpace')
        banner_enabled = dictionary.get('bannerEnabled')
        chassis_count = dictionary.get('chassisCount')
        cluster_audit_log_config = cohesity_management_sdk.models_v2.cluster_audit_log_config.ClusterAuditLogConfig.from_dictionary(
            dictionary.get('clusterAuditLogConfig')) if dictionary.get('clusterAuditLogConfig') else None
        cluster_size = dictionary.get('clusterSize')
        cluster_software_version = dictionary.get('clusterSoftwareVersion')
        cluster_type = dictionary.get('clusterType')
        created_time_msecs = dictionary.get('createdTimeMsecs')
        current_op_scheduled_time_secs = dictionary.get('currentOpScheduledTimeSecs')
        current_operation = dictionary.get('currentOperation')
        current_time_msecs = dictionary.get('currentTimeMsecs')
        description = dictionary.get('description')
        disk_count_by_tier = None
        if dictionary.get('diskCountByTier') is not None :
            disk_count_by_tier = list()
            for structure in dictionary.get('diskCountByTier') :
                disk_count_by_tier.append(
                    cohesity_management_sdk.models_v2.disk_count_by_tier.DiskCountByTier.from_dictionary(structure))
        dns_server_ips = dictionary.get('dnsServerIps')
        domain_names = dictionary.get('domainNames')
        enable_active_monitoring = dictionary.get('enableActiveMonitoring')
        enable_encryption = dictionary.get('enableEncryption')
        enable_patches_download = dictionary.get('enablePatchesDownload')
        enable_upgrade_pkg_polling = dictionary.get('enableUpgradePkgPolling')
        encryption_key_rotation_period_secs = dictionary.get('encryptionKeyRotationPeriodSecs')
        eula_config = cohesity_management_sdk.models_v2.eula_config.EulaConfig.from_dictionary(
            dictionary.get('eulaConfig')) if dictionary.get('eulaConfig') else None
        fault_tolerance_level = dictionary.get('faultToleranceLevel')
        file_services_audit_log_config = cohesity_management_sdk.models_v2.audit_log_config.AuditLogConfig.from_dictionary(
            dictionary.get('fileServicesAuditLogConfig')) if dictionary.get('fileServicesAuditLogConfig') else None
        gateway = dictionary.get('gateway')
        google_analytics_enabled = dictionary.get('googleAnalyticsEnabled')
        hardware_encryption_enabled = dictionary.get('hardwareEncryptionEnabled')
        hardware_info = cohesity_management_sdk.models_v2.cluster_hardware_info.ClusterHardwareInfo.from_dictionary(
            dictionary.get('hardwareInfo')) if dictionary.get('hardwareInfo') else None
        id = dictionary.get('id')
        incarnation_id = dictionary.get('incarnationId')
        ip_preference = dictionary.get('ipPreference')
        is_athena_subnet_clash = dictionary.get('isAthenaSubnetClash')
        is_cluster_mfa_enabled = dictionary.get('isClusterMfaEnabled')
        is_documentation_local = dictionary.get('isDocumentationLocal')
        is_patch_apply_aborted = dictionary.get('isPatchApplyAborted')
        is_patch_revert_aborted = dictionary.get('isPatchRevertAborted')
        is_upgrade_aborted = dictionary.get('isUpgradeAborted')
        kms_server_id = dictionary.get('kmsServerId')
        language_locale = dictionary.get('languageLocale')
        license_state = cohesity_management_sdk.models_v2.license_state.LicenseState.from_dictionary(
            dictionary.get('licenseState')) if dictionary.get('licenseState') else None
        load_balancer_vip_config = cohesity_management_sdk.models_v2.load_balancer_config.LoadBalancerConfig.from_dictionary(
            dictionary.get('loadBalancerVipConfig')) if dictionary.get('loadBalancerVipConfig') else None
        local_auth_domain_name = dictionary.get('localAuthDomainName')
        local_groups_enabled = dictionary.get('localGroupsEnabled')
        local_tenant_id = dictionary.get('localTenantId')
        metadata_fault_tolerance_factor = dictionary.get('metadataFaultToleranceFactor')
        minimum_failure_domains_needed = dictionary.get('minimumFailureDomainsNeeded')
        multi_tenancy_enabled = dictionary.get('multiTenancyEnabled')
        name = dictionary.get('name')
        network_config = cohesity_management_sdk.models_v2.cluster_network_config_3.ClusterNetworkConfig3.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None
        node_count = dictionary.get('nodeCount')
        node_ips = dictionary.get('nodeIps')
        ntp_settings = cohesity_management_sdk.models_v2.ntp_settings.NTPSettings.from_dictionary(
            dictionary.get('ntpSettings')) if dictionary.get('ntpSettings') else None
        patch_apply_failure_error_message = dictionary.get('patchApplyFailureErrorMessage')
        patch_revert_failure_error_message = dictionary.get('patchRevertFailureErrorMessage')
        patch_revert_version = dictionary.get('patchRevertVersion')
        patch_target_version = dictionary.get('patchTargetVersion')
        patch_v2_reverts_allowed = dictionary.get('patchV2RevertsAllowed')
        patch_version = dictionary.get('patchVersion')
        pcie_ssd_tier_rebalance_delay_secs = dictionary.get('pcieSsdTierRebalanceDelaySecs')
        proto_rpc_encryption_enabled = dictionary.get('protoRpcEncryptionEnabled')
        proxy_server_config = cohesity_management_sdk.models_v2.cluster_proxy_server_config.ClusterProxyServerConfig.from_dictionary(
            dictionary.get('proxyServerConfig')) if dictionary.get('proxyServerConfig') else None
        proxy_v_m_subnet = dictionary.get('proxyVMSubnet')
        region_id = dictionary.get('regionId')
        reverse_tunnel_enabled = dictionary.get('reverseTunnelEnabled')
        reverse_tunnel_end_time_msecs = dictionary.get('reverseTunnelEndTimeMsecs')
        rigel_cluster_params = cohesity_management_sdk.models_v2.rigel_cluster_params.RigelClusterParams.from_dictionary(
            dictionary.get('rigelClusterParams')) if dictionary.get('rigelClusterParams') else None
        s3_virtual_hosted_domain_names = dictionary.get('s3VirtualHostedDomainNames')
        sata_hdd_tier_admission_control = dictionary.get('sataHddTierAdmissionControl')
        schema_info_list = None
        if dictionary.get('schemaInfoList') is not None :
            schema_info_list = list()
            for structure in dictionary.get('schemaInfoList') :
                schema_info_list.append(
                    cohesity_management_sdk.models_v2.schema_info.SchemaInfo.from_dictionary(structure))
        security_mode_dod = dictionary.get('securityModeDod')
        smb_ad_disabled = dictionary.get('smbAdDisabled')
        smb_multichannel_enabled = dictionary.get('smbMultichannelEnabled')
        software_type = dictionary.get('softwareType')
        split_key_host_access = dictionary.get('splitKeyHostAccess')
        stats = cohesity_management_sdk.models_v2.cluster_stats.ClusterStats.from_dictionary(
            dictionary.get('stats')) if dictionary.get('stats') else None
        supported_config = cohesity_management_sdk.models_v2.supported_config.SupportedConfig.from_dictionary(
            dictionary.get('supportedConfig')) if dictionary.get('supportedConfig') else None
        sw_version = dictionary.get('swVersion')
        target_software_version = dictionary.get('targetSoftwareVersion')
        tenant_id = dictionary.get('tenantId')
        tenant_viewbox_sharing_enabled = dictionary.get('tenantViewboxSharingEnabled')
        timezone = dictionary.get('timezone')
        trust_domain = dictionary.get('trustDomain')
        turbo_mode = dictionary.get('turboMode')
        mtype = dictionary.get('type')
        upgrade_failure_error_string = dictionary.get('upgradeFailureErrorString')
        use_default_agent_ports = dictionary.get('useDefaultAgentPorts')
        use_heimdall = dictionary.get('useHeimdall')
        used_metadata_space_pct = dictionary.get('usedMetadataSpacePct')
        views_global_settings = cohesity_management_sdk.models_v2.views_global_settings.ViewsGlobalSettings.from_dictionary(
            dictionary.get('viewsGlobalSettings')) if dictionary.get('viewsGlobalSettings') else None
        message = dictionary.get('message')
        healthy_nodes = None
        if dictionary.get("healthyNodes") is not None:
            healthy_nodes = list()
            for structure in dictionary.get('healthyNodes'):
                healthy_nodes.append(cohesity_management_sdk.models_v2.node_specific_response.NodeSpecificResponse.from_dictionary(structure))
        unhealthy_nodes = None
        if dictionary.get("unhealthyNodes") is not None:
            unhealthy_nodes = list()
            for structure in dictionary.get('unhealthyNodes'):
                unhealthy_nodes.append(cohesity_management_sdk.models_v2.node_specific_response.NodeSpecificResponse.from_dictionary(structure))

        # Return an object of this model
        return cls(aes_encryption_mode,
                   amqp_target_config,
                   apps_subnet,
                   assigned_racks_count,
                   attempt_agent_ports_upgrade,
                   auth_support_for_pkg_downloads,
                   auth_type,
                   authorized_ssh_public_keys,
                   available_metadata_space,
                   banner_enabled,
                   chassis_count,
                   cluster_audit_log_config,
                   cluster_size,
                   cluster_software_version,
                   cluster_type,
                   created_time_msecs,
                   current_op_scheduled_time_secs,
                   current_operation,
                   current_time_msecs,
                   description,
                   disk_count_by_tier,
                   dns_server_ips,
                   domain_names,
                   enable_active_monitoring,
                   enable_encryption,
                   enable_patches_download,
                   enable_upgrade_pkg_polling,
                   encryption_key_rotation_period_secs,
                   eula_config,
                   fault_tolerance_level,
                   file_services_audit_log_config,
                   gateway,
                   google_analytics_enabled,
                   hardware_encryption_enabled,
                   hardware_info,
                   id,
                   incarnation_id,
                   ip_preference,
                   is_athena_subnet_clash,
                   is_cluster_mfa_enabled,
                   is_documentation_local,
                   is_patch_apply_aborted,
                   is_patch_revert_aborted,
                   is_upgrade_aborted,
                   kms_server_id,
                   language_locale,
                   license_state,
                   load_balancer_vip_config,
                   local_auth_domain_name,
                   local_groups_enabled,
                   local_tenant_id,
                   metadata_fault_tolerance_factor,
                   minimum_failure_domains_needed,
                   multi_tenancy_enabled,
                   name,
                   network_config,
                   node_count,
                   node_ips,
                   ntp_settings,
                   patch_apply_failure_error_message,
                   patch_revert_failure_error_message,
                   patch_revert_version,
                   patch_target_version,
                   patch_v2_reverts_allowed,
                   patch_version,
                   pcie_ssd_tier_rebalance_delay_secs,
                   proto_rpc_encryption_enabled,
                   proxy_server_config,
                   proxy_v_m_subnet,
                   region_id,
                   reverse_tunnel_enabled,
                   reverse_tunnel_end_time_msecs,
                   rigel_cluster_params,
                   s3_virtual_hosted_domain_names,
                   sata_hdd_tier_admission_control,
                   schema_info_list,
                   security_mode_dod,
                   smb_ad_disabled,
                   smb_multichannel_enabled,
                   software_type,
                   split_key_host_access,
                   stats,
                   supported_config,
                   sw_version,
                   target_software_version,
                   tenant_id,
                   tenant_viewbox_sharing_enabled,
                   timezone,
                   trust_domain,
                   turbo_mode,
                   mtype,
                   upgrade_failure_error_string,
                   use_default_agent_ports,
                   use_heimdall,
                   used_metadata_space_pct,
                   views_global_settings,
                   message,
                   healthy_nodes,
                   unhealthy_nodes)