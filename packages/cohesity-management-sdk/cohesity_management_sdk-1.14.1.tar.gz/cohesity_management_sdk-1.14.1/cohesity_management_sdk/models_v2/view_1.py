# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protocol_option
import cohesity_management_sdk.models_v2.qo_s
import cohesity_management_sdk.models_v2.subnet
import cohesity_management_sdk.models_v2.s_3_lifecycle_management
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
import cohesity_management_sdk.models_v2.filer_lifecycle_management
import cohesity_management_sdk.models_v2.view_intent
import cohesity_management_sdk.models_v2.bucket_policy
import cohesity_management_sdk.models_v2.owner_info_2
import cohesity_management_sdk.models_v2.view_protection
import cohesity_management_sdk.models_v2.view_alias_information
import cohesity_management_sdk.models_v2.view_failover
import cohesity_management_sdk.models_v2.view_stats
import cohesity_management_sdk.models_v2.view_share_permissions
import cohesity_management_sdk.models_v2.file_count
import cohesity_management_sdk.models_v2.view_pinning_config
import cohesity_management_sdk.models_v2.self_service_snapshot_config

class View1(object):

    """Implementation of the 'View.1' model.

    Specifies settings for defining a storage location (called a View)
    with NFS and SMB mount paths in a Storage Domain (View Box) on the
    Cohesity
    Cluster.

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
        lifecycle_management (S3LifecycleManagement): Specifies the S3 Lifecycle policy of the bucket
        owner_info (OwnerInfo2): Specifies the owner info of the View as an S3
            bucket.
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
        lexicographic_prefetch (bool): If small files are accessed sequentially from a
            client,this specifies whether to detect and prefetch files based on
            the lexicographic index to improve file read performance.
        file_lock_config (FileLevelDataLockConfigurations): Specifies a config
            to lock files in a view - to protect from malicious or an
            accidental attempt to delete or modify the files in this view.
        filer_lifecycle_management (list of FilerLifecycleManagement): Specifies the
            Lifecycle policy of this filer (NFS/SMB) view.
        file_extension_filter (FileExtensionFilter): TODO: type description
            here.
        antivirus_scan_config (AntivirusScanConfig): Specifies the antivirus
            scan config settings for this View.
        description (string): Specifies an optional text description about the
            View.
        intent (ViewIntent): Specifies the intent of the View.
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
        enable_metadata_accelerator (bool): Specifies if metadata accelerator is enabled
            for this view. Only supported while creating a view.
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
        view_pinning_config (ViewPinningConfig):  Specifies the pinning
            config of this view.
        self_service_snapshot_config (SelfServiceSnapshotConfig): Specifies
            self service config of this view.
        is_externally_triggered_backup_target (bool): Specifies whether the
            view is for externally triggered backup target. If so, Magneto
            will ignore the backup schedule for the view protection job of
            this view. By default it is disabled.
        enable_nfs_view_discovery (bool): If set, it enables discovery of view
            for NFS.
        enable_nfs_wcc (bool): If set, it enables NFS weak cache consistency.
        nfs_all_squash
            (NfsSquashSpecifiesTheSquashConfigForClientSubnetWhitelist): TODO:
            type description here.
        nfs_root_permissions (NfsRootPermissions): Specifies the config of NFS
            root permission of a view file system.
        nfs_root_squash
            (NfsSquashSpecifiesTheSquashConfigForClientSubnetWhitelist): TODO:
            type description here.
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
        smb_permissions_info (SMBPermissionsInformation): Specifies
            information about SMB permissions.
        share_permissions (ViewSharePermissions): Specifies share level
            permissions of the view.
        acl_config (AclConfig1): Specifies the ACL config of the View as an S3
            bucket.
        bucket_policy (BucketPolicy): Specifies the policy in effect for this bucket.
        owner_info (OwnerInfo2): Specifies the owner info of the View as an S3
            bucket.
        category (Category1Enum): Specifies the category of the View.
        name (string): Specifies the name of the View.
        view_id (long|int): Specifies an id of the View assigned by the
            Cohesity Cluster.
        is_category_inferred (bool): If True, category in response is not set
            by user but inferred by Iris because none is set. Category can
            only be none when view was created by v1 API or cloned from a view
            created by v1 API.  Inference Logic is as follows: 1. Object
            Services if only S3 or Swift protocol is selected. 2. Backup
            Target only if one read-write protocol is selected and    QoS is
            "Backup Target Commvault" or "Backup Target SSD". 3. File Services
            if there are more than 1 read-write protocol or    it doesn't fit
            any other category.
        storage_domain_id (long|int): Specifies the id of the Storage Domain
            (View Box) where the View is stored.
        storage_domain_name (string): Specifies the name of the Storage Domain
            (View Box) where the View is stored.
        create_time_msecs (long|int): Specifies the time that the View was
            created in milliseconds.
        basic_mount_path (string): Specifies the NFS mount path of the View
            (without the hostname information). This path is used to support
            NFS mounting of the paths specified in the nfsExportPathList on
            Windows systems.
        nfs_mount_path (string):This field is currently deprecated. Please use
            NFS MountPaths which would be an array of strings
        nfs_mount_paths (list of string): Array of NFS Paths. Specifies the
            path for mounting this  View as an NFS share. If Kerberos Provider
            has multiple hostaliases, each host alias has\n its own path.
        smb_mount_paths (list of string): Array of SMB Paths. Specifies the
            possible paths that can be used to mount this View as a SMB share.
            If Active Directory has multiple account names; each machine
            account has its own path.
        case_insensitive_names_enabled (bool): Specifies whether to support
            case insensitive file/folder names. This parameter can only be set
            during create and cannot be changed.
        view_protection (ViewProtection): Specifies information about the
            Protection Groups that are protecting the View.
        data_lock_expiry_usecs (long|int): DataLock (Write Once Read Many)
            lock expiry epoch time in microseconds. If a view is marked as a
            DataLock view, only a Data Security Officer (a user having Data
            Security Privilege) can delete the view until the lock expiry
            time.
        aliases (list of ViewAliasInformation): Aliases created for the view.
            A view alias allows a directory path inside a view to be mounted
            using the alias name.
        basic_mount_path (string): Specifies the NFS mount path of the View (without the hostname
            information).This path is used to support NFS mounting of the paths specified in the
            nfsExportPathList on Windows systems.
        is_target_for_migrated_data (bool): Specifies if a view contains
            migrated data.
        view_failover (ViewFailover): Specifies the information about the
            failover of the view.
        s_3_folder_support_enabled (bool): Specifies whether to support s3 folder support feature. This
            parameter can only be set during create and cannot be changed.
        stats (ViewStats): Provides statistics about the View.
        file_count_by_size (list of FileCount): Specifies the file count by
            size for the View.
        owner_sid (string): Specifies the sid of the view owner.
        object_services_mapping_config (ObjectServicesMappingConfigEnum):
            Specifies the Object Services key mapping config of the view. This
            parameter can only be set during create and cannot be changed.
            Configuration of Object Services key mapping. Specifies the type
            of Object Services key mapping config.
        s_3_access_path (string): Specifies the path to access this View as an
            S3 share.
        swift_user_domain (string): Specifies the Keystone user domain.
        swift_username (string): Specifies the Keystone username.
        versioning (VersioningEnum): Specifies the versioning state of S3
            bucket. Buckets can be in one of three states: UnVersioned
            (default), VersioningEnabled, or VersioningSuspended. Once
            versioning is enabled for a bucket, it can never return to an
            UnVersioned state. However, versioning on the bucket can be
            suspended.

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
        "lexicographic_prefetch" : 'lexicographicPrefetch' ,
        "file_lock_config":'fileLockConfig',
        "filer_lifecycle_management" : 'filerLifecycleManagement' ,
        "file_extension_filter":'fileExtensionFilter',
        "antivirus_scan_config":'antivirusScanConfig',
        "description":'description',
        "intent" : 'intent' ,
        "allow_mount_on_windows":'allowMountOnWindows',
        "enable_minion":'enableMinion',
        "enable_filer_audit_logging":'enableFilerAuditLogging',
        "tenant_id":'tenantId',
        "enable_live_indexing":'enableLiveIndexing',
        "enable_metadata_accelerator" : 'enableMetadataAccelerator' ,
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
        "enable_nfs_unix_authentication":'enableNfsUnixAuthentication',
        "enable_nfs_kerberos_authentication":'enableNfsKerberosAuthentication',
        "enable_nfs_kerberos_integrity":'enableNfsKerberosIntegrity',
        "enable_nfs_kerberos_privacy":'enableNfsKerberosPrivacy',
        "enable_smb_view_discovery":'enableSmbViewDiscovery',
        "enable_nfs_wcc" : 'enableNfsWcc' ,
        "enable_smb_access_based_enumeration":'enableSmbAccessBasedEnumeration',
        "enable_smb_encryption":'enableSmbEncryption',
        "enforce_smb_encryption":'enforceSmbEncryption',
        "enable_fast_durable_handle":'enableFastDurableHandle',
        "enable_smb_oplock":'enableSmbOplock',
        "smb_permissions_info":'smbPermissionsInfo',
        "share_permissions":'sharePermissions',
        "acl_config":'aclConfig',
        "bucket_policy" : 'bucketPolicy' ,
        "enable_abac" : 'enableAbac' ,
        "lifecycle_management":'lifecycleManagement',
        "owner_info":'ownerInfo',
        "category":'category',
        "name":'name',
        "view_id":'viewId',
        "is_category_inferred":'isCategoryInferred',
        "storage_domain_id":'storageDomainId',
        "storage_domain_name":'storageDomainName',
        "create_time_msecs":'createTimeMsecs',
        "basic_mount_path":'basicMountPath',
        "nfs_mount_path":'nfsMountPath',
        "nfs_mount_paths":'nfsMountPaths',
        "smb_mount_paths":'smbMountPaths',
        "case_insensitive_names_enabled":'caseInsensitiveNamesEnabled',
        "view_protection":'viewProtection',
        "data_lock_expiry_usecs":'dataLockExpiryUsecs',
        "aliases":'aliases',
        "is_target_for_migrated_data":'isTargetForMigratedData',
        "view_failover":'viewFailover',
        "s_3_folder_support_enabled":'s3FolderSupportEnabled',
        "stats":'stats',
        "file_count_by_size":'fileCountBySize',
        "owner_sid":'ownerSid',
        "object_services_mapping_config":'objectServicesMappingConfig',
        "s_3_access_path":'s3AccessPath',
        "swift_user_domain":'swiftUserDomain',
        "swift_username":'swiftUsername',
        "versioning":'versioning'
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
                 lexicographic_prefetch=None ,
                 file_lock_config=None,
                 filer_lifecycle_management=None ,
                 file_extension_filter=None,
                 antivirus_scan_config=None,
                 description=None,
                 intent=None ,
                 allow_mount_on_windows=None,
                 enable_minion=None,
                 enable_filer_audit_logging=None,
                 tenant_id=None,
                 enable_live_indexing=None,
                 enable_metadata_accelerator=None ,
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
                 enable_nfs_wcc=None ,
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
                 acl_config=None,
                 bucket_policy=None,
                 enable_abac=None ,
                 lifecycle_management=None,
                 owner_info=None,
                 category=None,
                 name=None,
                 view_id=None,
                 is_category_inferred=None,
                 storage_domain_id=None,
                 storage_domain_name=None,
                 create_time_msecs=None,
                 basic_mount_path=None,
                 nfs_mount_path=None,
                 nfs_mount_paths=None,
                 smb_mount_paths=None,
                 case_insensitive_names_enabled=None,
                 view_protection=None,
                 data_lock_expiry_usecs=None,
                 aliases=None,
                 is_target_for_migrated_data=None,
                 view_failover=None,
                 s_3_folder_support_enabled=None,
                 stats=None,
                 file_count_by_size=None,
                 owner_sid=None,
                 object_services_mapping_config=None,
                 s_3_access_path=None,
                 swift_user_domain=None,
                 swift_username=None,
                 versioning=None):
        """Constructor for the View1 class"""

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
        self.lexicographic_prefetch = lexicographic_prefetch
        self.file_lock_config = file_lock_config
        self.filer_lifecycle_management = filer_lifecycle_management
        self.file_extension_filter = file_extension_filter
        self.antivirus_scan_config = antivirus_scan_config
        self.description = description
        self.intent = intent
        self.allow_mount_on_windows = allow_mount_on_windows
        self.enable_minion = enable_minion
        self.enable_filer_audit_logging = enable_filer_audit_logging
        self.tenant_id = tenant_id
        self.enable_live_indexing = enable_live_indexing
        self.enable_metadata_accelerator = enable_metadata_accelerator
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
        self.enable_nfs_unix_authentication = enable_nfs_unix_authentication
        self.enable_nfs_kerberos_authentication = enable_nfs_kerberos_authentication
        self.enable_nfs_kerberos_integrity = enable_nfs_kerberos_integrity
        self.enable_nfs_kerberos_privacy = enable_nfs_kerberos_privacy
        self.enable_smb_view_discovery = enable_smb_view_discovery
        self.enable_nfs_wcc = enable_nfs_wcc
        self.enable_smb_access_based_enumeration = enable_smb_access_based_enumeration
        self.enable_smb_encryption = enable_smb_encryption
        self.enforce_smb_encryption = enforce_smb_encryption
        self.enable_fast_durable_handle = enable_fast_durable_handle
        self.enable_smb_oplock = enable_smb_oplock
        self.smb_permissions_info = smb_permissions_info
        self.share_permissions = share_permissions
        self.acl_config = acl_config
        self.bucket_policy = bucket_policy
        self.enable_abac = enable_abac
        self.lifecycle_management = lifecycle_management
        self.owner_info = owner_info
        self.category = category
        self.name = name
        self.view_id = view_id
        self.is_category_inferred = is_category_inferred
        self.storage_domain_id = storage_domain_id
        self.storage_domain_name = storage_domain_name
        self.create_time_msecs = create_time_msecs
        self.basic_mount_path = basic_mount_path
        self.nfs_mount_path = nfs_mount_path
        self.nfs_mount_paths = nfs_mount_paths
        self.smb_mount_paths = smb_mount_paths
        self.case_insensitive_names_enabled = case_insensitive_names_enabled
        self.view_protection = view_protection
        self.data_lock_expiry_usecs = data_lock_expiry_usecs
        self.aliases = aliases
        self.is_target_for_migrated_data = is_target_for_migrated_data
        self.view_failover = view_failover
        self.s_3_folder_support_enabled = s_3_folder_support_enabled
        self.stats = stats
        self.file_count_by_size = file_count_by_size
        self.owner_sid = owner_sid
        self.object_services_mapping_config = object_services_mapping_config
        self.s_3_access_path = s_3_access_path
        self.swift_user_domain = swift_user_domain
        self.swift_username = swift_username
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
        lexicographic_prefetch = dictionary.get('lexicographicPrefetch')
        file_lock_config = cohesity_management_sdk.models_v2.file_level_data_lock_configurations.FileLevelDataLockConfigurations.from_dictionary(dictionary.get('fileLockConfig')) if dictionary.get('fileLockConfig') else None
        filer_lifecycle_management = cohesity_management_sdk.models_v2.filer_lifecycle_management.FilerLifecycleManagement.from_dictionary(
            dictionary.get('filerLifecycleManagement')) if dictionary.get('filerLifecycleManagement') else None
        file_extension_filter = cohesity_management_sdk.models_v2.file_extension_filter.FileExtensionFilter.from_dictionary(dictionary.get('fileExtensionFilter')) if dictionary.get('fileExtensionFilter') else None
        antivirus_scan_config = cohesity_management_sdk.models_v2.antivirus_scan_config.AntivirusScanConfig.from_dictionary(dictionary.get('antivirusScanConfig')) if dictionary.get('antivirusScanConfig') else None
        description = dictionary.get('description')
        intent = cohesity_management_sdk.models_v2.view_intent.ViewIntent.from_dictionary(
            dictionary.get('intent')) if dictionary.get('intent') else None
        allow_mount_on_windows = dictionary.get('allowMountOnWindows')
        enable_minion = dictionary.get('enableMinion')
        enable_filer_audit_logging = dictionary.get('enableFilerAuditLogging')
        tenant_id = dictionary.get('tenantId')
        enable_live_indexing = dictionary.get('enableLiveIndexing')
        enable_metadata_accelerator = dictionary.get('enableMetadataAccelerator')
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
        enable_nfs_unix_authentication = dictionary.get('enableNfsUnixAuthentication')
        enable_nfs_kerberos_authentication = dictionary.get('enableNfsKerberosAuthentication')
        enable_nfs_kerberos_integrity = dictionary.get('enableNfsKerberosIntegrity')
        enable_nfs_kerberos_privacy = dictionary.get('enableNfsKerberosPrivacy')
        enable_smb_view_discovery = dictionary.get('enableSmbViewDiscovery')
        enable_nfs_wcc = dictionary.get('enableNfsWcc')
        enable_smb_access_based_enumeration = dictionary.get('enableSmbAccessBasedEnumeration')
        enable_smb_encryption = dictionary.get('enableSmbEncryption')
        enforce_smb_encryption = dictionary.get('enforceSmbEncryption')
        enable_fast_durable_handle = dictionary.get('enableFastDurableHandle')
        enable_smb_oplock = dictionary.get('enableSmbOplock')
        smb_permissions_info = cohesity_management_sdk.models_v2.smb_permissions_information.SMBPermissionsInformation.from_dictionary(dictionary.get('smbPermissionsInfo')) if dictionary.get('smbPermissionsInfo') else None
        share_permissions = cohesity_management_sdk.models_v2.view_share_permissions.ViewSharePermissions.from_dictionary(dictionary.get('sharePermissions')) if dictionary.get('sharePermissions') else None
        acl_config = cohesity_management_sdk.models_v2.acl_config_1.AclConfig1.from_dictionary(dictionary.get('aclConfig')) if dictionary.get('aclConfig') else None
        bucket_policy = cohesity_management_sdk.models_v2.bucket_policy.BucketPolicy.from_dictionary(
            dictionary.get('bucketPolicy')) if dictionary.get('bucketPolicy') else None
        enable_abac = dictionary.get('enableAbac')
        lifecycle_management = cohesity_management_sdk.models_v2.s_3_lifecycle_management.S3LifecycleManagement.from_dictionary(dictionary.get('lifecycleManagement')) if dictionary.get('lifecycleManagement') else None
        owner_info = cohesity_management_sdk.models_v2.owner_info_2.OwnerInfo2.from_dictionary(dictionary.get('ownerInfo')) if dictionary.get('ownerInfo') else None
        category = dictionary.get('category')
        name = dictionary.get('name')
        view_id = dictionary.get('viewId')
        is_category_inferred = dictionary.get('isCategoryInferred')
        storage_domain_id = dictionary.get('storageDomainId')
        storage_domain_name = dictionary.get('storageDomainName')
        create_time_msecs = dictionary.get('createTimeMsecs')
        basic_mount_path = dictionary.get('basicMountPath')
        nfs_mount_path = dictionary.get('nfsMountPath')
        nfs_mount_paths = dictionary.get('nfsMountPaths')
        smb_mount_paths = dictionary.get('smbMountPaths')
        case_insensitive_names_enabled = dictionary.get('caseInsensitiveNamesEnabled')
        view_protection = cohesity_management_sdk.models_v2.view_protection.ViewProtection.from_dictionary(dictionary.get('viewProtection')) if dictionary.get('viewProtection') else None
        data_lock_expiry_usecs = dictionary.get('dataLockExpiryUsecs')
        aliases = None
        if dictionary.get("aliases") is not None:
            aliases = list()
            for structure in dictionary.get('aliases'):
                aliases.append(cohesity_management_sdk.models_v2.view_alias_information.ViewAliasInformation.from_dictionary(structure))
        is_target_for_migrated_data = dictionary.get('isTargetForMigratedData')
        view_failover = cohesity_management_sdk.models_v2.view_failover.ViewFailover.from_dictionary(dictionary.get('viewFailover')) if dictionary.get('viewFailover') else None
        s_3_folder_support_enabled = dictionary.get('s3FolderSupportEnabled')
        stats = cohesity_management_sdk.models_v2.view_stats.ViewStats.from_dictionary(dictionary.get('stats')) if dictionary.get('stats') else None
        file_count_by_size = None
        if dictionary.get("fileCountBySize") is not None:
            file_count_by_size = list()
            for structure in dictionary.get('fileCountBySize'):
                file_count_by_size.append(cohesity_management_sdk.models_v2.file_count.FileCount.from_dictionary(structure))
        owner_sid = dictionary.get('ownerSid')
        object_services_mapping_config = dictionary.get('objectServicesMappingConfig')
        s_3_access_path = dictionary.get('s3AccessPath')
        swift_user_domain = dictionary.get('swiftUserDomain')
        swift_username = dictionary.get('swiftUsername')
        versioning = dictionary.get('versioning')

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
                   lexicographic_prefetch ,
                   file_lock_config,
                   filer_lifecycle_management,
                   file_extension_filter,
                   antivirus_scan_config,
                   description,
                   intent,
                   allow_mount_on_windows,
                   enable_minion,
                   enable_filer_audit_logging,
                   tenant_id,
                   enable_live_indexing,
                   enable_metadata_accelerator,
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
                   enable_nfs_wcc,
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
                   acl_config,
                   bucket_policy,
                   enable_abac,
                   lifecycle_management,
                   owner_info,
                   category,
                   name,
                   view_id,
                   is_category_inferred,
                   storage_domain_id,
                   storage_domain_name,
                   create_time_msecs,
                   basic_mount_path,
                   nfs_mount_path,
                   nfs_mount_paths,
                   smb_mount_paths,
                   case_insensitive_names_enabled,
                   view_protection,
                   data_lock_expiry_usecs,
                   aliases,
                   is_target_for_migrated_data,
                   view_failover,
                   s_3_folder_support_enabled,
                   stats,
                   file_count_by_size,
                   owner_sid,
                   object_services_mapping_config,
                   s_3_access_path,
                   swift_user_domain,
                   swift_username,
                   versioning)