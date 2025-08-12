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
import cohesity_management_sdk.models_v2.nfs_squash_specifies_the_squash_config_for_client_subnet_whitelist
import cohesity_management_sdk.models_v2.nfs_root_permissions
import cohesity_management_sdk.models_v2.smb_permissions_information
import cohesity_management_sdk.models_v2.smb_permission
import cohesity_management_sdk.models_v2.acl_config_1
import cohesity_management_sdk.models_v2.owner_info_2
import cohesity_management_sdk.models_v2.view_share_permissions
import cohesity_management_sdk.models_v2.view_pinning_config
import cohesity_management_sdk.models_v2.self_service_snapshot_config


class UpdateViewParam(object):

    """Implementation of the 'UpdateViewParam' model.

    Specifies the settings that define a View.

    Attributes:
        name (string): Specifies the name of the View.
        category (Category1Enum): Specifies the category of the View.
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
        file_lock_config (FileLockConfig): Optional config that enables file
            locking for this view. It cannot be disabled during the edit of a
            view, if it has been enabled during the creation of the view.
            Also, it cannot be enabled if it was disabled during the creation
            of the view.
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
        is_read_only (bool): Specifies if the view is a read only view. User
            will no longer be able to write to this view if this is set to
            true.
        view_pinning_config (ViewPinningConfig): Specifies the pinning config
            of this view.
        self_service_snapshot_config (SelfServiceSnapshotConfig): Specifies
            self service config of this view.
        is_externally_triggered_backup_target (bool): Specifies whether the
            view is for externally triggered backup target. If so, Magneto
            will ignore the backup schedule for the view protection job of
            this view. By default it is disabled.
        enable_nfs_view_discovery (bool): If set, it enables discovery of view
            for NFS.
        nfs_all_squash
            (NfsSquashSpecifiesTheSquashConfigForClientSubnetWhitelist): TODO:
            type description here.
        nfs_root_permissions (NfsRootPermissions): Specifies the config of NFS
            root permission of a view file system.
        nfs_root_squash
            (NfsSquashSpecifiesTheSquashConfigForClientSubnetWhitelist): TODO:
            type description here.
        enable_smb_view_discovery (bool): If set, it enables discovery of view
            for SMB.
        enable_smb_access_based_enumeration (bool): Specifies if access-based
            enumeration should be enabled. If 'true', only files and folders
            that the user has permissions to access are visible on the SMB
            share for that user.
        enable_smb_encryption (bool): Specifies the SMB encryption for the
            View. If set, it enables the SMB encryption for the View.
            Encryption is supported only by SMB 3.x dialects. Dialects that do
            not support would still access data in unencrypted format.
        enforce_smb_encryption (bool): Specifies the SMB encryption for all
            the sessions for the View. If set, encryption is enforced for all
            the sessions for the View. When enabled all future and existing
            unencrypted sessions are disallowed.
        enable_fast_durable_handle (bool): Specifies whether fast durable
            handle is enabled. If enabled, view open handle will be kept in
            memory, which results in a higher performance. But the handles
            cannot be recovered if node or service crashes.
        enable_smb_oplock (bool): Specifies whether SMB opportunistic lock is
            enabled.
        smb_permissions_info (SMBPermissionsInformation): Specifies
            information about SMB permissions.
        share_permissions (list of SMBPermission): Specifies a list of share
            level permissions.
        s3_access_path (string): Specifies the path to access this View as an
            S3 share.
        acl_config (AclConfig1): Specifies the ACL config of the View as an S3
            bucket.
        owner_info (OwnerInfo2): Specifies the owner info of the View as an S3
            bucket.
        versioning (VersioningEnum): Specifies the versioning state of S3
            bucket. Buckets can be in one of three states: UnVersioned
            (default), VersioningEnabled, or VersioningSuspended. Once
            versioning is enabled for a bucket, it can never return to an
            UnVersioned state. However, versioning on the bucket can be
            suspended.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "category":'category',
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
        "is_read_only":'isReadOnly',
        "view_pinning_config":'viewPinningConfig',
        "self_service_snapshot_config":'selfServiceSnapshotConfig',
        "is_externally_triggered_backup_target":'isExternallyTriggeredBackupTarget',
        "enable_nfs_view_discovery":'enableNfsViewDiscovery',
        "nfs_all_squash":'nfsAllSquash',
        "nfs_root_permissions":'nfsRootPermissions',
        "nfs_root_squash":'nfsRootSquash',
        "enable_smb_view_discovery":'enableSmbViewDiscovery',
        "enable_smb_access_based_enumeration":'enableSmbAccessBasedEnumeration',
        "enable_smb_encryption":'enableSmbEncryption',
        "enforce_smb_encryption":'enforceSmbEncryption',
        "enable_fast_durable_handle":'enableFastDurableHandle',
        "enable_smb_oplock":'enableSmbOplock',
        "smb_permissions_info":'smbPermissionsInfo',
        "share_permissions":'sharePermissions',
        "s3_access_path":'s3AccessPath',
        "acl_config":'aclConfig',
        "owner_info":'ownerInfo',
        "versioning":'versioning'
    }

    def __init__(self,
                 name=None,
                 category=None,
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
                 is_read_only=None,
                 view_pinning_config=None,
                 self_service_snapshot_config=None,
                 is_externally_triggered_backup_target=None,
                 enable_nfs_view_discovery=None,
                 nfs_all_squash=None,
                 nfs_root_permissions=None,
                 nfs_root_squash=None,
                 enable_smb_view_discovery=None,
                 enable_smb_access_based_enumeration=None,
                 enable_smb_encryption=None,
                 enforce_smb_encryption=None,
                 enable_fast_durable_handle=None,
                 enable_smb_oplock=None,
                 smb_permissions_info=None,
                 share_permissions=None,
                 s3_access_path=None,
                 acl_config=None,
                 owner_info=None,
                 versioning=None):
        """Constructor for the UpdateViewParam class"""

        # Initialize members of the class
        self.name = name
        self.protocol_access = protocol_access
        self.category = category
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
        self.is_read_only = is_read_only
        self.view_pinning_config = view_pinning_config
        self.self_service_snapshot_config = self_service_snapshot_config
        self.is_externally_triggered_backup_target = is_externally_triggered_backup_target
        self.enable_nfs_view_discovery = enable_nfs_view_discovery
        self.nfs_all_squash = nfs_all_squash
        self.nfs_root_permissions = nfs_root_permissions
        self.nfs_root_squash = nfs_root_squash
        self.enable_smb_view_discovery = enable_smb_view_discovery
        self.enable_smb_access_based_enumeration = enable_smb_access_based_enumeration
        self.enable_smb_encryption = enable_smb_encryption
        self.enforce_smb_encryption = enforce_smb_encryption
        self.enable_fast_durable_handle = enable_fast_durable_handle
        self.enable_smb_oplock = enable_smb_oplock
        self.smb_permissions_info = smb_permissions_info
        self.share_permissions = share_permissions
        self.s3_access_path = s3_access_path
        self.acl_config = acl_config
        self.owner_info = owner_info
        self.versioning = versioning


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
        name = dictionary.get('name')
        category = dictionary.get('category')
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
        is_read_only = dictionary.get('isReadOnly')
        view_pinning_config = cohesity_management_sdk.models_v2.view_pinning_config.ViewPinningConfig.from_dictionary(dictionary.get('viewPinningConfig')) if dictionary.get('viewPinningConfig') else None
        self_service_snapshot_config = cohesity_management_sdk.models_v2.self_service_snapshot_config.SelfServiceSnapshotConfig.from_dictionary(dictionary.get('selfServiceSnapshotConfig')) if dictionary.get('selfServiceSnapshotConfig') else None
        is_externally_triggered_backup_target = dictionary.get('isExternallyTriggeredBackupTarget')
        enable_nfs_view_discovery = dictionary.get('enableNfsViewDiscovery')
        nfs_all_squash = cohesity_management_sdk.models_v2.nfs_squash_specifies_the_squash_config_for_client_subnet_whitelist.NfsSquashSpecifiesTheSquashConfigForClientSubnetWhitelist.from_dictionary(dictionary.get('nfsAllSquash')) if dictionary.get('nfsAllSquash') else None
        nfs_root_permissions = cohesity_management_sdk.models_v2.nfs_root_permissions.NfsRootPermissions.from_dictionary(dictionary.get('nfsRootPermissions')) if dictionary.get('nfsRootPermissions') else None
        nfs_root_squash = cohesity_management_sdk.models_v2.nfs_squash_specifies_the_squash_config_for_client_subnet_whitelist.NfsSquashSpecifiesTheSquashConfigForClientSubnetWhitelist.from_dictionary(dictionary.get('nfsRootSquash')) if dictionary.get('nfsRootSquash') else None
        enable_smb_view_discovery = dictionary.get('enableSmbViewDiscovery')
        enable_smb_access_based_enumeration = dictionary.get('enableSmbAccessBasedEnumeration')
        enable_smb_encryption = dictionary.get('enableSmbEncryption')
        enforce_smb_encryption = dictionary.get('enforceSmbEncryption')
        enable_fast_durable_handle = dictionary.get('enableFastDurableHandle')
        enable_smb_oplock = dictionary.get('enableSmbOplock')
        smb_permissions_info = cohesity_management_sdk.models_v2.smb_permissions_information.SMBPermissionsInformation.from_dictionary(dictionary.get('smbPermissionsInfo')) if dictionary.get('smbPermissionsInfo') else None
        share_permissions = cohesity_management_sdk.models_v2.view_share_permissions.ViewSharePermissions.from_dictionary(dictionary.get('sharePermissions')) if dictionary.get('sharePermissions') else None
        s3_access_path = dictionary.get('s3AccessPath')
        acl_config = cohesity_management_sdk.models_v2.acl_config_1.AclConfig1.from_dictionary(dictionary.get('aclConfig')) if dictionary.get('aclConfig') else None
        owner_info = cohesity_management_sdk.models_v2.owner_info_2.OwnerInfo2.from_dictionary(dictionary.get('ownerInfo')) if dictionary.get('ownerInfo') else None
        versioning = dictionary.get('versioning')

        # Return an object of this model
        return cls(name,
                   category,
                   protocol_access,
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
                   is_read_only,
                   view_pinning_config,
                   self_service_snapshot_config,
                   is_externally_triggered_backup_target,
                   enable_nfs_view_discovery,
                   nfs_all_squash,
                   nfs_root_permissions,
                   nfs_root_squash,
                   enable_smb_view_discovery,
                   enable_smb_access_based_enumeration,
                   enable_smb_encryption,
                   enforce_smb_encryption,
                   enable_fast_durable_handle,
                   enable_smb_oplock,
                   smb_permissions_info,
                   share_permissions,
                   s3_access_path,
                   acl_config,
                   owner_info,
                   versioning)


