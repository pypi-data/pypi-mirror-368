# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models_v2.file_filtering_policy
import cohesity_management_sdk.models_v2.data_tiering_target
import cohesity_management_sdk.models_v2.file_size_policy
import cohesity_management_sdk.models_v2.file_level_data_lock_configurations
import cohesity_management_sdk.models_v2.filter_ip_configuration
import cohesity_management_sdk.models_v2.snapshot_label
import cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration
import cohesity_management_sdk.models.file_uptiering_params_source_view_map_entry
import cohesity_management_sdk.models_v2.uptiering_file_age_policy
import cohesity_management_sdk.models_v2.downtiering_file_age_policy

class NasEnvJobParams(object) :
    """Implementation of the 'NasEnvJobParams' model.

    Specifies additional special parameters that are applicable only to Types of 'kGenericNas' type.

    Attributes:
        backup_existing_snapshot (bool): Specifies that snapshot label is not set for Data-Protect Netapp
            Volumes backup. If field is set to true, existing oldest snapshot is used
            for backup and subsequent incremental will be selected in ascending order
            of snapshot create time on the source. If snapshot label is set, this
            field is set to false.
        continue_on_error (bool): Specifies whether or not the Protection Group should continue
            regardless of whether or not an error was encountered during protection
            group run.
        enable_faster_incremental_backups (bool): Specifies whether this job will enable faster incremental backups
            using change list or similar APIs
        encryption_enabled (bool): Specifies whether the protection group should use encryption
            while backup or not.
        file_lock_config (FileLevelDataLockConfigurations): Optional config that enables file locking for this view. It
            cannot be disabled during the edit of a view, if it has been enabled during
            the creation of the view. Also, it cannot be enabled if it was disabled
            during the creation of the view.
        file_path_filters (FileFilteringPolicy): Specifies filters on the backup objects like files and directories.
            Specifying filters decide which objects within a source should be backed
            up. If this field is not specified, then all of the objects within the
            source will be backed up.
        filter_ip_config (FilterIPConfiguration): Specifies the list of IP addresses that are allowed or denied
            at the job level. Allowed IPs and Denied IPs cannot be used together.
        modify_source_permissions (bool): Specifies if the NAS source permissions should be modified
            internally to allow backups.
        nas_protocol (NasProtocolEnum): Specifies the preferred protocol to use if this device supports
            multiple protocols.
        nfs_version_preference (NfsVersionPreferenceEnum): Specifies the preference of NFS version to be backed up if
            a volume supports multiple versions of NFS.
        snapshot_label (SnapshotLabel): Specifies the incremental and full snapshot label for Data-Protect
            Netapp Volumes backup. If snapMirrorConfig is provided then snapshotLabel
            should not be provided.
        throttling_config (NasSourceAndProtectionThrottlingConfiguration): Specifies the source throttling parameters to be used during
            full or incremental backup of the NAS source.
        use_change_list (bool): Specify whether to use the Isilon Changelist API to directly
            discover changed files/directories for faster incremental backup. Cohesity
            will keep an extra snapshot which will be deleted by the next successful
            backup.
        enable_audit_logging (bool): Specifies whether to audit log the file
            tiering activity.
        file_size (FileSizePolicy): Specifies the file's selection rule by
            file size eg. 1. select files greather than 10 Bytes. 2. select
            files less than 20 TiB. 3. select files greather than 5 MiB. type:
            object
        file_path (FileFilteringPolicy): Specifies a set of filters for a file
            based Protection Group. These values are strings which can
            represent a prefix or suffix. Example: '/tmp' or '*.mp4'. For file
            based Protection Groups, all files under prefixes specified by the
            'includeFilters' list will be protected unless they are explicitly
            excluded by the 'excludeFilters' list.
        include_all_files (bool): If set, all files in the view will be uptiered regardless
            of file_select_policy, num_file_access, hot_file_window, file_size
            constraints.
        target (DataTieringTarget): Specifies target for data tiering.
        uptiering_file_age (UptieringFileAgePolicy): TODO: type description here.
        auto_orphan_data_cleanup (bool): Specifies whether to remove the orphan data from the target
            if the symlink is removed from the source.
        downtiering_file_age (DowntieringFileAgePolicy): TODO: type description here.
        skip_back_symlink (bool): Specifies whether to create a symlink for the migrated data
            from source to target.
    """

    _names = {
        "backup_existing_snapshot":'backupExistingSnapshot',
        "continue_on_error":'continueOnError',
        "enable_faster_incremental_backups":'enableFasterIncrementalBackups',
        "encryption_enabled":'encryptionEnabled',
        "file_lock_config":'fileLockConfig',
        "file_path_filters":'filePathFilters',
        "filter_ip_config":'filterIpConfig',
        "modify_source_permissions":'modifySourcePermissions',
        "nas_protocol":'nasProtocol',
        "nfs_version_preference":'nfsVersionPreference',
        "snapshot_label":'snapshotLabel',
        "throttling_config":'throttlingConfig',
        "use_change_list":'useChangeList',
        "enable_audit_logging":'enableAuditLogging',
        "file_path":'filePath',
        "file_size":'fileSize',
        "include_all_files":'includeAllFiles',
        "target":'target',
        "uptiering_file_age":'uptieringFileAge',
        "auto_orphan_data_cleanup":'autoOrphanDataCleanup',
        "downtiering_file_age":'downtieringFileAge',
        "skip_back_symlink":"skipBackSymlink"
    }

    def __init__(self,
                 backup_existing_snapshot=None,
                 continue_on_error=None,
                 enable_faster_incremental_backups=None,
                 encryption_enabled=None,
                 file_lock_config=None,
                 file_path_filters=None,
                 filter_ip_config=None,
                 modify_source_permissions=None,
                 nas_protocol=None,
                 nfs_version_preference=None,
                 snapshot_label=None,
                 throttling_config=None,
                 use_change_list =None,
                 enable_audit_logging=False,
                 file_path=None ,
                 file_size=None,
                 include_all_files=None,
                 target=None,
                 uptiering_file_age=None,
                 auto_orphan_data_cleanup=None,
                 downtiering_file_age=None,
                 skip_back_symlink=None
                 ) :
        """Constructor for the NasEnvJobParams class"""

        # Initialize members of the class
        self.backup_existing_snapshot = backup_existing_snapshot
        self.continue_on_error = continue_on_error
        self.enable_faster_incremental_backups = enable_faster_incremental_backups
        self.encryption_enabled = encryption_enabled
        self.file_lock_config = file_lock_config
        self.file_path_filters = file_path_filters
        self.filter_ip_config = filter_ip_config
        self.modify_source_permissions = modify_source_permissions
        self.nas_protocol = nas_protocol
        self.nfs_version_preference = nfs_version_preference
        self.snapshot_label = snapshot_label
        self.throttling_config = throttling_config
        self.use_change_list = use_change_list
        self.enable_audit_logging = enable_audit_logging
        self.file_path = file_path
        self.file_size = file_size
        self.include_all_files = include_all_files
        self.target = target
        self.uptiering_file_age = uptiering_file_age
        self.auto_orphan_data_cleanup = auto_orphan_data_cleanup
        self.downtiering_file_age = downtiering_file_age
        self.skip_back_symlink = skip_back_symlink

    @classmethod
    def from_dictionary(cls , dictionary) :
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None :
            return None

        backup_existing_snapshot = dictionary.get('backupExistingSnapshot')
        continue_on_error = dictionary.get('continueOnError')
        enable_faster_incremental_backups = dictionary.get('enableFasterIncrementalBackups')
        encryption_enabled = dictionary.get('encryptionEnabled')
        file_lock_config = cohesity_management_sdk.models_v2.file_level_data_lock_configurations.FileLevelDataLockConfigurations.from_dictionary(
            dictionary.get('fileLockConfig')) if dictionary.get('fileLockConfig') else None
        file_path_filters = cohesity_management_sdk.models_v2.file_filtering_policy.FileFilteringPolicy.from_dictionary(dictionary.get('filePathFilters')) if dictionary.get('filePathFilters') else None
        filter_ip_config = cohesity_management_sdk.models_v2.filter_ip_configuration.FilterIPConfiguration.from_dictionary(dictionary.get('filterIpConfig')) if dictionary.get('filterIpConfig') else None
        modify_source_permissions = dictionary.get('modifySourcePermissions')
        nas_protocol = dictionary.get('nasProtocol')
        nfs_version_preference = dictionary.get('nfsVersionPreference')
        snapshot_label = cohesity_management_sdk.models_v2.snapshot_label.SnapshotLabel.from_dictionary(dictionary.get('snapshotLabel')) if dictionary.get('snapshotLabel') else None
        throttling_config = cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration.NasSourceAndProtectionThrottlingConfiguration.from_dictionary(
            dictionary.get('throttlingConfig')) if dictionary.get('throttlingConfig') else None
        use_change_list = dictionary.get('useChangeList')
        enable_audit_logging = dictionary.get("enableAuditLogging") if dictionary.get("enableAuditLogging") else False
        file_path = cohesity_management_sdk.models_v2.file_filtering_policy.FileFilteringPolicy.from_dictionary(
            dictionary.get('filePath')) if dictionary.get('filePath') else None
        file_size = cohesity_management_sdk.models_v2.file_size_policy.FileSizePolicy.from_dictionary(
            dictionary.get('fileSize')) if dictionary.get('fileSize') else None
        include_all_files = dictionary.get('includeAllFiles')
        target = cohesity_management_sdk.models_v2.data_tiering_target.DataTieringTarget.from_dictionary(
            dictionary.get('target')) if dictionary.get('target') else None
        uptiering_file_age = cohesity_management_sdk.models_v2.uptiering_file_age_policy.UptieringFileAgePolicy.from_dictionary(
            dictionary.get('uptieringFileAge')) if dictionary.get('uptieringFileAge') else None
        auto_orphan_data_cleanup = dictionary.get('autoOrphanDataCleanup')
        downtiering_file_age = cohesity_management_sdk.models_v2.downtiering_file_age_policy.DowntieringFileAgePolicy.from_dictionary(dictionary.get('downtieringFileAge')) if dictionary.get('downtieringFileAge') else None
        skip_back_symlink = dictionary.get('skipBackSymlink')

        return cls(
            backup_existing_snapshot,
            continue_on_error,
            enable_faster_incremental_backups,
            encryption_enabled,
            file_lock_config,
            file_path_filters,
            filter_ip_config,
            modify_source_permissions,
            nas_protocol,
            nfs_version_preference,
            snapshot_label,
            throttling_config,
            use_change_list,
            enable_audit_logging,
            file_path,
            file_size,
            include_all_files,
            target,
            uptiering_file_age,
            auto_orphan_data_cleanup,
            downtiering_file_age,
            skip_back_symlink
        )