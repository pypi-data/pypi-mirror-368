# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protocol_option
import cohesity_management_sdk.models_v2.qo_s
import cohesity_management_sdk.models_v2.subnet
import cohesity_management_sdk.models_v2.nis_netgroups
import cohesity_management_sdk.models_v2.storage_policy_override
import cohesity_management_sdk.models_v2.quota_policy
import cohesity_management_sdk.models_v2.file_level_data_lock_configurations
import cohesity_management_sdk.models_v2.file_extension_filter
import cohesity_management_sdk.models_v2.antivirus_scan_config

class BasicViewParams(object):

    """Implementation of the 'Basic View Params.' model.

    Basic View Params

    Attributes:
        protocol_access (list of ProtocolOption): Specifies the supported
            Protocols for the View.
        qos (QoS): Specifies the Quality of Service (QoS) Policy for the
            View.
        override_global_subnet_whitelist (bool): Specifies whether view level
            client subnet whitelist overrides cluster and global setting.
        subnet_whitelist (list of Subnet): Array of Subnets. Specifies a list
            of Subnets with IP addresses that have permissions to access the
            View. (Overrides or extends the Subnets specified at the global
            Cohesity Cluster level.)
        override_global_netgroup_whitelist (bool): Specifies whether view
            level client netgroup whitelist overrides cluster and global
            setting.
        netgroup_whitelist (NisNetgroups): Response of NIS Netgroups.
        security_mode (SecurityModeEnum): Specifies the security mode used for
            this view. Currently we support the following modes: Native,
            Unified and NTFS style. 'NativeMode' indicates a native security
            mode. 'UnifiedMode' indicates a unified security mode. 'NtfsMode'
            indicates a NTFS style security mode.
        storage_policy_override (StoragePolicyOverride): Specifies if inline
            deduplication and compression settings inherited from Storage
            Domain (View Box) should be disabled for this View.
        logical_quota (QuotaPolicy): Specifies a quota limit that can be
            optionally applied to Views and Storage Domains. At the View
            level, this quota defines a logical limit for usage on the View.
            At the Storage Domain level, this quota defines a physical limit
            or a default logical View limit. If a physical quota is specified
            for Storage Domain, this quota defines a physical limit for the
            usage on the Storage Domain. If a default logical View quota is
            specified for Storage Domain, this limit is inherited by all the
            Views in that Storage Domain. However, this inherited quota can be
            overwritten at the View level. A new write is not allowed if the
            resource will exceed the specified quota. However, it takes time
            for the Cohesity Cluster to calculate the usage across Nodes, so
            the limit may be exceeded by a small amount. In addition, if the
            limit is increased or data is removed, there may be a delay before
            the Cohesity Cluster allows more data to be written to the
            resource, as the Cluster calculates the usage across Nodes.
        file_lock_config (FileLevelDataLockConfigurations): Specifies a config
            to lock files in a view - to protect from malicious or an
            accidental attempt to delete or modify the files in this view.
        file_extension_filter (FileExtensionFilter): TODO: type description
            here.
        antivirus_scan_config (AntivirusScanConfig): Specifies the antivirus
            scan config settings for this View.
        description (string): Specifies an optional text description about the
            View.
        allow_mount_on_windows (bool): Specifies if this View can be mounted
            using the NFS protocol on Windows systems. If true, this View can
            be NFS mounted on Windows systems. hidden: true
        enable_minion (bool): Specifies if this view should allow minion or
            not. If true, this will allow minion. hidden: true
        enable_filer_audit_logging (bool): Specifies if Filer Audit Logging is
            enabled for this view.
        tenant_id (string): Optional tenant id who has access to this View.
        enable_live_indexing (bool): Specifies whether to enable live indexing
            for the view.
        enable_offline_caching (bool): Specifies whether to enable offline
            file caching of the view.
        swift_project_domain (string): Specifies the Keystone project domain.
        swift_project_name (string): Specifies the Keystone project name.
        access_sids (list of string): Array of Security Identifiers (SIDs)
            Specifies the list of security identifiers (SIDs) for the
            restricted Principals who have access to this View.
        view_lock_enabled (bool): Specifies whether view lock is enabled. If
            enabled the view cannot be modified or deleted until unlock. By
            default it is disabled.
        is_externally_triggered_backup_target (bool): Specifies whether the
            view is for externally triggered backup target. If so, Magneto
            will ignore the backup schedule for the view protection job of
            this view. By default it is disabled.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protocol_access":'protocolAccess',
        "qos":'qos',
        "override_global_subnet_whitelist":'overrideGlobalSubnetWhitelist',
        "subnet_whitelist":'subnetWhitelist',
        "override_global_netgroup_whitelist":'overrideGlobalNetgroupWhitelist',
        "netgroup_whitelist":'netgroupWhitelist',
        "security_mode":'securityMode',
        "storage_policy_override":'storagePolicyOverride',
        "logical_quota":'logicalQuota',
        "file_lock_config":'fileLockConfig',
        "file_extension_filter":'fileExtensionFilter',
        "antivirus_scan_config":'antivirusScanConfig',
        "description":'description',
        "allow_mount_on_windows":'allowMountOnWindows',
        "enable_minion":'enableMinion',
        "enable_filer_audit_logging":'enableFilerAuditLogging',
        "tenant_id":'tenantId',
        "enable_live_indexing":'enableLiveIndexing',
        "enable_offline_caching":'enableOfflineCaching',
        "swift_project_domain":'swiftProjectDomain',
        "swift_project_name":'swiftProjectName',
        "access_sids":'accessSids',
        "view_lock_enabled":'viewLockEnabled',
        "is_externally_triggered_backup_target":'isExternallyTriggeredBackupTarget'
    }

    def __init__(self,
                 protocol_access=None,
                 qos=None,
                 override_global_subnet_whitelist=None,
                 subnet_whitelist=None,
                 override_global_netgroup_whitelist=None,
                 netgroup_whitelist=None,
                 security_mode=None,
                 storage_policy_override=None,
                 logical_quota=None,
                 file_lock_config=None,
                 file_extension_filter=None,
                 antivirus_scan_config=None,
                 description=None,
                 allow_mount_on_windows=None,
                 enable_minion=None,
                 enable_filer_audit_logging=None,
                 tenant_id=None,
                 enable_live_indexing=None,
                 enable_offline_caching=None,
                 swift_project_domain=None,
                 swift_project_name=None,
                 access_sids=None,
                 view_lock_enabled=None,
                 is_externally_triggered_backup_target=None):
        """Constructor for the BasicViewParams class"""

        # Initialize members of the class
        self.protocol_access = protocol_access
        self.qos = qos
        self.override_global_subnet_whitelist = override_global_subnet_whitelist
        self.subnet_whitelist = subnet_whitelist
        self.override_global_netgroup_whitelist = override_global_netgroup_whitelist
        self.netgroup_whitelist = netgroup_whitelist
        self.security_mode = security_mode
        self.storage_policy_override = storage_policy_override
        self.logical_quota = logical_quota
        self.file_lock_config = file_lock_config
        self.file_extension_filter = file_extension_filter
        self.antivirus_scan_config = antivirus_scan_config
        self.description = description
        self.allow_mount_on_windows = allow_mount_on_windows
        self.enable_minion = enable_minion
        self.enable_filer_audit_logging = enable_filer_audit_logging
        self.tenant_id = tenant_id
        self.enable_live_indexing = enable_live_indexing
        self.enable_offline_caching = enable_offline_caching
        self.swift_project_domain = swift_project_domain
        self.swift_project_name = swift_project_name
        self.access_sids = access_sids
        self.view_lock_enabled = view_lock_enabled
        self.is_externally_triggered_backup_target = is_externally_triggered_backup_target


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
        protocol_access = None
        if dictionary.get("protocolAccess") is not None:
            protocol_access = list()
            for structure in dictionary.get('protocolAccess'):
                protocol_access.append(cohesity_management_sdk.models_v2.protocol_option.ProtocolOption.from_dictionary(structure))
        qos = cohesity_management_sdk.models_v2.qo_s.QoS.from_dictionary(dictionary.get('qos')) if dictionary.get('qos') else None
        override_global_subnet_whitelist = dictionary.get('overrideGlobalSubnetWhitelist')
        subnet_whitelist = None
        if dictionary.get("subnetWhitelist") is not None:
            subnet_whitelist = list()
            for structure in dictionary.get('subnetWhitelist'):
                subnet_whitelist.append(cohesity_management_sdk.models_v2.subnet.Subnet.from_dictionary(structure))
        override_global_netgroup_whitelist = dictionary.get('overrideGlobalNetgroupWhitelist')
        netgroup_whitelist = cohesity_management_sdk.models_v2.nis_netgroups.NisNetgroups.from_dictionary(dictionary.get('netgroupWhitelist')) if dictionary.get('netgroupWhitelist') else None
        security_mode = dictionary.get('securityMode')
        storage_policy_override = cohesity_management_sdk.models_v2.storage_policy_override.StoragePolicyOverride.from_dictionary(dictionary.get('storagePolicyOverride')) if dictionary.get('storagePolicyOverride') else None
        logical_quota = cohesity_management_sdk.models_v2.quota_policy.QuotaPolicy.from_dictionary(dictionary.get('logicalQuota')) if dictionary.get('logicalQuota') else None
        file_lock_config = cohesity_management_sdk.models_v2.file_level_data_lock_configurations.FileLevelDataLockConfigurations.from_dictionary(dictionary.get('fileLockConfig')) if dictionary.get('fileLockConfig') else None
        file_extension_filter = cohesity_management_sdk.models_v2.file_extension_filter.FileExtensionFilter.from_dictionary(dictionary.get('fileExtensionFilter')) if dictionary.get('fileExtensionFilter') else None
        antivirus_scan_config = cohesity_management_sdk.models_v2.antivirus_scan_config.AntivirusScanConfig.from_dictionary(dictionary.get('antivirusScanConfig')) if dictionary.get('antivirusScanConfig') else None
        description = dictionary.get('description')
        allow_mount_on_windows = dictionary.get('allowMountOnWindows')
        enable_minion = dictionary.get('enableMinion')
        enable_filer_audit_logging = dictionary.get('enableFilerAuditLogging')
        tenant_id = dictionary.get('tenantId')
        enable_live_indexing = dictionary.get('enableLiveIndexing')
        enable_offline_caching = dictionary.get('enableOfflineCaching')
        swift_project_domain = dictionary.get('swiftProjectDomain')
        swift_project_name = dictionary.get('swiftProjectName')
        access_sids = dictionary.get('accessSids')
        view_lock_enabled = dictionary.get('viewLockEnabled')
        is_externally_triggered_backup_target = dictionary.get('isExternallyTriggeredBackupTarget')

        # Return an object of this model
        return cls(protocol_access,
                   qos,
                   override_global_subnet_whitelist,
                   subnet_whitelist,
                   override_global_netgroup_whitelist,
                   netgroup_whitelist,
                   security_mode,
                   storage_policy_override,
                   logical_quota,
                   file_lock_config,
                   file_extension_filter,
                   antivirus_scan_config,
                   description,
                   allow_mount_on_windows,
                   enable_minion,
                   enable_filer_audit_logging,
                   tenant_id,
                   enable_live_indexing,
                   enable_offline_caching,
                   swift_project_domain,
                   swift_project_name,
                   access_sids,
                   view_lock_enabled,
                   is_externally_triggered_backup_target)


