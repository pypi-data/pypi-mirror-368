# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protocol_option
import cohesity_management_sdk.models_v2.qo_s
import cohesity_management_sdk.models_v2.subnet
import cohesity_management_sdk.models_v2.netgroup_whitelist
import cohesity_management_sdk.models_v2.storage_policy_override_2
import cohesity_management_sdk.models_v2.logical_quota
import cohesity_management_sdk.models_v2.file_lock_config
import cohesity_management_sdk.models_v2.file_extension_filter_2
import cohesity_management_sdk.models_v2.antivirus_scan_config
import cohesity_management_sdk.models_v2.view_pinning_config_2
import cohesity_management_sdk.models_v2.self_service_snapshot_config_2
import cohesity_management_sdk.models_v2.nfs_all_squash
import cohesity_management_sdk.models_v2.nfs_root_permissions_2
import cohesity_management_sdk.models_v2.nfs_root_squash
import cohesity_management_sdk.models_v2.smb_permissions_info
import cohesity_management_sdk.models_v2.share_permissions

class CreateView(object):

    """Implementation of the 'Create View.' model.

    Specifies the information required for creating a new View w/o required
    fields.

    Attributes:
        storage_domain_id (long|int): Specifies the id of the Storage Domain
            (View Box) where the View will be created.
        case_insensitive_names_enabled (bool): Specifies whether to support
            case insensitive file/folder names. This parameter can only be set
            during create and cannot be changed.
        object_services_mapping_config (ObjectServicesMappingConfigEnum):
            Specifies the Object Services key mapping config of the view. This
            parameter can only be set during create and cannot be changed.
            Configuration of Object Services key mapping. Specifies the type
            of Object Services key mapping config.
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
        netgroup_whitelist (NetgroupWhitelist): Array of Netgroups. Specifies
            a list of netgroups with domains that have permissions to access
            the View. (Overrides or extends the Netgroup specified at the
            global Cohesity Cluster level.)
        security_mode (SecurityModeEnum): Specifies the security mode used for
            this view. Currently we support the following modes: Native,
            Unified and NTFS style. 'NativeMode' indicates a native security
            mode. 'UnifiedMode' indicates a unified security mode. 'NtfsMode'
            indicates a NTFS style security mode.
        storage_policy_override (StoragePolicyOverride2): Specifies if inline
            deduplication and compression settings inherited from the Storage
            Domain (View Box) should be disabled for this View.
        logical_quota (LogicalQuota): Specifies an optional logical quota
            limit (in bytes) for the usage allowed on this View. (Logical data
            is when the data is fully hydrated and expanded.) This limit
            overrides the limit inherited from the Storage Domain (View Box)
            (if set). If logicalQuota is nil, the limit is inherited from the
            Storage Domain (View Box) (if set). A new write is not allowed if
            the Storage Domain (View Box) will exceed the specified quota.
            However, it takes time for the Cohesity Cluster to calculate the
            usage across Nodes, so the limit may be exceeded by a small
            amount. In addition, if the limit is increased or data is removed,
            there may be a delay before the Cohesity Cluster allows more data
            to be written to the View, as the Cluster is calculating the usage
            across Nodes.
        file_lock_config (FileLockConfig): Optional config that enables file
            locking for this view. It cannot be disabled during the edit of a
            view, if it has been enabled during the creation of the view.
            Also, it cannot be enabled if it was disabled during the creation
            of the view.
        file_extension_filter (FileExtensionFilter2): Optional filtering
            criteria that should be satisfied by all the files created in this
            view. It does not affect existing files.
        antivirus_scan_config (AntivirusScanConfig): Specifies the antivirus
            scan config settings for this View.
        description (string): Specifies an optional text description about the
            View.
        allow_mount_on_windows (bool): Specifies if this View can be mounted
            using the NFS protocol on Windows systems. If true, this View can
            be NFS mounted on Windows systems.
        enable_minion (bool): Specifies if this view should allow minion or
            not. If true, this will allow minion.
        enable_filer_audit_logging (bool): Specifies if Filer Audit Logging is
            enabled for this view.
        tenant_id (string): Optional tenant id who has access to this View.
        enable_live_indexing (bool): Specifies whether to enable live indexing
            for the view.
        enable_offline_caching (bool): Specifies whether to enable offline
            file caching of the view.
        access_sids (list of string): Array of Security Identifiers (SIDs)
            Specifies the list of security identifiers (SIDs) for the
            restricted Principals who have access to this View.
        view_lock_enabled (bool): Specifies whether view lock is enabled. If
            enabled the view cannot be modified or deleted until unlock. By
            default it is disabled.
        is_read_only (bool): Specifies if the view is a read only view. User
            will no longer be able to write to this view if this is set to
            true.
        view_pinning_config (ViewPinningConfig2): Specifies the pinning config
            of this view.
        self_service_snapshot_config (SelfServiceSnapshotConfig2): Specifies
            self service config of this view.
        is_externally_triggered_backup_target (bool): Specifies whether the
            view is for externally triggered backup target. If so, Magneto
            will ignore the backup schedule for the view protection job of
            this view. By default it is disabled.
        enable_nfs_view_discovery (bool): If set, it enables discovery of view
            for NFS.
        nfs_all_squash (NfsAllSquash): Specifies the NFS all squash config.
        nfs_root_permissions (NfsRootPermissions2): Specifies the NFS root
            permission config of the view file system.
        nfs_root_squash (NfsRootSquash): Specifies the NFS root squash
            config.
        enable_nfs_unix_authentication (bool): If set, it enables NFS UNIX
            Authentication
        enable_nfs_kerberos_authentication (bool): If set, it enables NFS
            Kerberos Authentication
        enable_nfs_kerberos_integrity (bool): If set, it enables NFS Kerberos
            Integrity
        enable_nfs_kerberos_privacy (bool): If set, it enables NFS Kerberos
            Privacy
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
        smb_permissions_info (SmbPermissionsInfo): Specifies the SMB
            permissions for the View.
        share_permissions (SharePermissions): Specifies share level
            permissions of the view.
        s_3_access_path (string): Specifies the path to access this View as an
            S3 share.
        swift_project_domain (string): Specifies the Keystone project domain.
        swift_project_name (string): Specifies the Keystone project name.
        swift_user_domain (string): Specifies the Keystone user domain.
        swift_username (string): Specifies the Keystone username.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "storage_domain_id":'storageDomainId',
        "case_insensitive_names_enabled":'caseInsensitiveNamesEnabled',
        "object_services_mapping_config":'objectServicesMappingConfig',
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
        "enable_nfs_unix_authentication":'enableNfsUnixAuthentication',
        "enable_nfs_kerberos_authentication":'enableNfsKerberosAuthentication',
        "enable_nfs_kerberos_integrity":'enableNfsKerberosIntegrity',
        "enable_nfs_kerberos_privacy":'enableNfsKerberosPrivacy',
        "enable_smb_view_discovery":'enableSmbViewDiscovery',
        "enable_smb_access_based_enumeration":'enableSmbAccessBasedEnumeration',
        "enable_smb_encryption":'enableSmbEncryption',
        "enforce_smb_encryption":'enforceSmbEncryption',
        "enable_fast_durable_handle":'enableFastDurableHandle',
        "enable_smb_oplock":'enableSmbOplock',
        "smb_permissions_info":'smbPermissionsInfo',
        "share_permissions":'sharePermissions',
        "s_3_access_path":'s3AccessPath',
        "swift_project_domain":'swiftProjectDomain',
        "swift_project_name":'swiftProjectName',
        "swift_user_domain":'swiftUserDomain',
        "swift_username":'swiftUsername'
    }

    def __init__(self,
                 storage_domain_id=None,
                 case_insensitive_names_enabled=None,
                 object_services_mapping_config=None,
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
                 enable_nfs_unix_authentication=None,
                 enable_nfs_kerberos_authentication=None,
                 enable_nfs_kerberos_integrity=None,
                 enable_nfs_kerberos_privacy=None,
                 enable_smb_view_discovery=None,
                 enable_smb_access_based_enumeration=None,
                 enable_smb_encryption=None,
                 enforce_smb_encryption=None,
                 enable_fast_durable_handle=None,
                 enable_smb_oplock=None,
                 smb_permissions_info=None,
                 share_permissions=None,
                 s_3_access_path=None,
                 swift_project_domain=None,
                 swift_project_name=None,
                 swift_user_domain=None,
                 swift_username=None):
        """Constructor for the CreateView class"""

        # Initialize members of the class
        self.storage_domain_id = storage_domain_id
        self.case_insensitive_names_enabled = case_insensitive_names_enabled
        self.object_services_mapping_config = object_services_mapping_config
        self.name = name
        self.category = category
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
        self.enable_nfs_unix_authentication = enable_nfs_unix_authentication
        self.enable_nfs_kerberos_authentication = enable_nfs_kerberos_authentication
        self.enable_nfs_kerberos_integrity = enable_nfs_kerberos_integrity
        self.enable_nfs_kerberos_privacy = enable_nfs_kerberos_privacy
        self.enable_smb_view_discovery = enable_smb_view_discovery
        self.enable_smb_access_based_enumeration = enable_smb_access_based_enumeration
        self.enable_smb_encryption = enable_smb_encryption
        self.enforce_smb_encryption = enforce_smb_encryption
        self.enable_fast_durable_handle = enable_fast_durable_handle
        self.enable_smb_oplock = enable_smb_oplock
        self.smb_permissions_info = smb_permissions_info
        self.share_permissions = share_permissions
        self.s_3_access_path = s_3_access_path
        self.swift_project_domain = swift_project_domain
        self.swift_project_name = swift_project_name
        self.swift_user_domain = swift_user_domain
        self.swift_username = swift_username


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
        storage_domain_id = dictionary.get('storageDomainId')
        case_insensitive_names_enabled = dictionary.get('caseInsensitiveNamesEnabled')
        object_services_mapping_config = dictionary.get('objectServicesMappingConfig')
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
        netgroup_whitelist = cohesity_management_sdk.models_v2.netgroup_whitelist.NetgroupWhitelist.from_dictionary(dictionary.get('netgroupWhitelist')) if dictionary.get('netgroupWhitelist') else None
        security_mode = dictionary.get('securityMode')
        storage_policy_override = cohesity_management_sdk.models_v2.storage_policy_override_2.StoragePolicyOverride2.from_dictionary(dictionary.get('storagePolicyOverride')) if dictionary.get('storagePolicyOverride') else None
        logical_quota = cohesity_management_sdk.models_v2.logical_quota.LogicalQuota.from_dictionary(dictionary.get('logicalQuota')) if dictionary.get('logicalQuota') else None
        file_lock_config = cohesity_management_sdk.models_v2.file_lock_config.FileLockConfig.from_dictionary(dictionary.get('fileLockConfig')) if dictionary.get('fileLockConfig') else None
        file_extension_filter = cohesity_management_sdk.models_v2.file_extension_filter_2.FileExtensionFilter2.from_dictionary(dictionary.get('fileExtensionFilter')) if dictionary.get('fileExtensionFilter') else None
        antivirus_scan_config = cohesity_management_sdk.models_v2.antivirus_scan_config.AntivirusScanConfig.from_dictionary(dictionary.get('antivirusScanConfig')) if dictionary.get('antivirusScanConfig') else None
        description = dictionary.get('description')
        allow_mount_on_windows = dictionary.get('allowMountOnWindows')
        enable_minion = dictionary.get('enableMinion')
        enable_filer_audit_logging = dictionary.get('enableFilerAuditLogging')
        tenant_id = dictionary.get('tenantId')
        enable_live_indexing = dictionary.get('enableLiveIndexing')
        enable_offline_caching = dictionary.get('enableOfflineCaching')
        access_sids = dictionary.get('accessSids')
        view_lock_enabled = dictionary.get('viewLockEnabled')
        is_read_only = dictionary.get('isReadOnly')
        view_pinning_config = cohesity_management_sdk.models_v2.view_pinning_config_2.ViewPinningConfig2.from_dictionary(dictionary.get('viewPinningConfig')) if dictionary.get('viewPinningConfig') else None
        self_service_snapshot_config = cohesity_management_sdk.models_v2.self_service_snapshot_config_2.SelfServiceSnapshotConfig2.from_dictionary(dictionary.get('selfServiceSnapshotConfig')) if dictionary.get('selfServiceSnapshotConfig') else None
        is_externally_triggered_backup_target = dictionary.get('isExternallyTriggeredBackupTarget')
        enable_nfs_view_discovery = dictionary.get('enableNfsViewDiscovery')
        nfs_all_squash = cohesity_management_sdk.models_v2.nfs_all_squash.NfsAllSquash.from_dictionary(dictionary.get('nfsAllSquash')) if dictionary.get('nfsAllSquash') else None
        nfs_root_permissions = cohesity_management_sdk.models_v2.nfs_root_permissions_2.NfsRootPermissions2.from_dictionary(dictionary.get('nfsRootPermissions')) if dictionary.get('nfsRootPermissions') else None
        nfs_root_squash = cohesity_management_sdk.models_v2.nfs_root_squash.NfsRootSquash.from_dictionary(dictionary.get('nfsRootSquash')) if dictionary.get('nfsRootSquash') else None
        enable_nfs_unix_authentication = dictionary.get('enableNfsUnixAuthentication')
        enable_nfs_kerberos_authentication = dictionary.get('enableNfsKerberosAuthentication')
        enable_nfs_kerberos_integrity = dictionary.get('enableNfsKerberosIntegrity')
        enable_nfs_kerberos_privacy = dictionary.get('enableNfsKerberosPrivacy')
        enable_smb_view_discovery = dictionary.get('enableSmbViewDiscovery')
        enable_smb_access_based_enumeration = dictionary.get('enableSmbAccessBasedEnumeration')
        enable_smb_encryption = dictionary.get('enableSmbEncryption')
        enforce_smb_encryption = dictionary.get('enforceSmbEncryption')
        enable_fast_durable_handle = dictionary.get('enableFastDurableHandle')
        enable_smb_oplock = dictionary.get('enableSmbOplock')
        smb_permissions_info = cohesity_management_sdk.models_v2.smb_permissions_info.SmbPermissionsInfo.from_dictionary(dictionary.get('smbPermissionsInfo')) if dictionary.get('smbPermissionsInfo') else None
        share_permissions = cohesity_management_sdk.models_v2.share_permissions.SharePermissions.from_dictionary(dictionary.get('sharePermissions')) if dictionary.get('sharePermissions') else None
        s_3_access_path = dictionary.get('s3AccessPath')
        swift_project_domain = dictionary.get('swiftProjectDomain')
        swift_project_name = dictionary.get('swiftProjectName')
        swift_user_domain = dictionary.get('swiftUserDomain')
        swift_username = dictionary.get('swiftUsername')

        # Return an object of this model
        return cls(storage_domain_id,
                   case_insensitive_names_enabled,
                   object_services_mapping_config,
                   name,
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
                   enable_nfs_unix_authentication,
                   enable_nfs_kerberos_authentication,
                   enable_nfs_kerberos_integrity,
                   enable_nfs_kerberos_privacy,
                   enable_smb_view_discovery,
                   enable_smb_access_based_enumeration,
                   enable_smb_encryption,
                   enforce_smb_encryption,
                   enable_fast_durable_handle,
                   enable_smb_oplock,
                   smb_permissions_info,
                   share_permissions,
                   s_3_access_path,
                   swift_project_domain,
                   swift_project_name,
                   swift_user_domain,
                   swift_username)


