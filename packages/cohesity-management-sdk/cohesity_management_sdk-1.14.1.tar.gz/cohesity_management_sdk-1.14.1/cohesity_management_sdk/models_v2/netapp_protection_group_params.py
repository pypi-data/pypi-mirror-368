# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.netapp_protection_group_object_params
import cohesity_management_sdk.models_v2.snapshot_label
import cohesity_management_sdk.models_v2.snap_mirror_config
import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.file_level_data_lock_configurations
import cohesity_management_sdk.models_v2.protection_group_file_filtering_policy
import cohesity_management_sdk.models_v2.host_based_backup_script_params
import cohesity_management_sdk.models_v2.continuous_snapshot_params
import cohesity_management_sdk.models_v2.filter_ip_configuration
import cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration

class NetappProtectionGroupParams(object):

    """Implementation of the 'NetappProtectionGroupParams' model.

    Specifies the parameters which are specific to Netapp related Protection
    Groups.

    Attributes:
        objects (list of NetappProtectionGroupObjectParams): Specifies the
            objects to be included in the Protection Group.
        exclude_object_ids (list of long|int): Specifies the objects to be
            excluded in the Protection Group.
        direct_cloud_archive (bool): Specifies whether or not to store the
            snapshots in this run directly in an Archive Target instead of on
            the Cluster. If this is set to true, the associated policy must
            have exactly one Archive Target associated with it and the policy
            must be set up to archive after every run. Also, a Storage Domain
            cannot be specified. Default behavior is 'false'.
        native_format (bool): Specifies whether or not to enable native format
            for direct archive job. This field is set to true if native format
            should be used for archiving.
        nfs_version_preference (NfsVersionPreferenceEnum): Specifies the preference of NFS version to be backed up if a
          volume supports multiple versions of NFS.
        snapshot_label (SnapshotLabel): Specifies the snapshot label for
            incremental and full backup of Secondary Netapp volumes
            (Data-Protect Volumes).
        snap_mirror_config (SnapMirrorConfig): Specifies the snapshot backup
            configuration if S3 views are used for backing up NetApp
            Data-Protect volumes.
        backup_existing_snapshot (bool): Specifies that snapshot label is not
            set for Data-Protect Netapp Volumes backup. If field is set to
            true, existing oldest snapshot is used for backup and subsequent
            incremental will be selected in ascending order of snapshot create
            time on the source. If snapshot label is set, this field is set to
            false.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        protocol (ProtocolEnum): Specifies the preferred protocol to use if
            this device supports multiple protocols.
        continue_on_error (bool): Specifies whether or not the Protection
            Group should continue regardless of whether or not an error was
            encountered during protection group run.
        continuous_snapshots (ContinuousSnapshotParams): Specifies the source snapshots to be taken even if there is a
          pending run in a protection group.
        encryption_enabled (bool): Specifies whether the protection group
            should use encryption while backup or not.
        file_lock_config (FileLevelDataLockConfigurations): Specifies a config
            to lock files in a view - to protect from malicious or an
            accidental attempt to delete or modify the files in this view.
        file_filters (ProtectionGroupFileFilteringPolicy): Specifies a set of
            filters for a file based Protection Group. These values are
            strings which can represent a prefix or suffix. Example: '/tmp' or
            '*.mp4'. For file based Protection Groups, all files under
            prefixes specified by the 'includeFilters' list will be protected
            unless they are explicitly excluded by the 'excludeFilters' list.
        filter_ip_config (FilterIpConfig): Specifies the list of IP addresses that are allowed or denied
          at the job level. Allowed IPs and Denied IPs cannot be used together.
        modify_source_permissions (bool): Specifies if the Isilon source permissions should be modified
          internally to allow backups.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.
        pre_post_script (HostBasedBackupScriptParams): Specifies params of a
            pre/post scripts to be executed before and after a backup run.
        throttling_config (NasThrottlingConfig): Specifies the source throttling parameters to be used during
          full or incremental backup of the NAS source.
        use_changelist (bool): Specify whether to use the Isilon Changelist API to directly
          discover changed files/directories for faster incremental backup. Cohesity
          will keep an extra snapshot which will be deleted by the next successful
          backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "exclude_object_ids":'excludeObjectIds',
        "direct_cloud_archive":'directCloudArchive',
        "native_format":'nativeFormat',
        "nfs_version_preference":'nfsVersionPreference',
        "snapshot_label":'snapshotLabel',
        "snap_mirror_config":'snapMirrorConfig',
        "backup_existing_snapshot":'backupExistingSnapshot',
        "indexing_policy":'indexingPolicy',
        "protocol":'protocol',
        "continue_on_error":'continueOnError',
        "continuous_snapshots":'continuousSnapshots',
        "encryption_enabled":'encryptionEnabled',
        "file_lock_config":'fileLockConfig',
        "file_filters":'fileFilters',
        "filter_ip_config":'filterIpConfig',
        "modify_source_permissions":'modifySourcePermissions',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "pre_post_script":'prePostScript',
        "throttling_config":'throttlingConfig',
        "use_changelist":'useChangelist'
    }

    def __init__(self,
                 objects=None,
                 exclude_object_ids=None,
                 direct_cloud_archive=None,
                 native_format=None,
                 nfs_version_preference=None,
                 snapshot_label=None,
                 snap_mirror_config=None,
                 backup_existing_snapshot=None,
                 indexing_policy=None,
                 protocol=None,
                 continue_on_error=None,
                 continuous_snapshots=None,
                 encryption_enabled=None,
                 file_lock_config=None,
                 file_filters=None,
                 filter_ip_config=None,
                 modify_source_permissions=None,
                 source_id=None,
                 source_name=None,
                 pre_post_script=None,
                 throttling_config=None,
                 use_changelist=None):
        """Constructor for the NetappProtectionGroupParams class"""

        # Initialize members of the class
        self.objects = objects
        self.exclude_object_ids = exclude_object_ids
        self.direct_cloud_archive = direct_cloud_archive
        self.native_format = native_format
        self.nfs_version_preference = nfs_version_preference
        self.snapshot_label = snapshot_label
        self.snap_mirror_config = snap_mirror_config
        self.backup_existing_snapshot = backup_existing_snapshot
        self.indexing_policy = indexing_policy
        self.protocol = protocol
        self.continue_on_error = continue_on_error
        self.continuous_snapshots = continuous_snapshots
        self.encryption_enabled = encryption_enabled
        self.file_lock_config = file_lock_config
        self.file_filters = file_filters
        self.filter_ip_config = filter_ip_config
        self.modify_source_permissions = modify_source_permissions
        self.source_id = source_id
        self.source_name = source_name
        self.pre_post_script = pre_post_script
        self.throttling_config = throttling_config
        self.use_changelist = use_changelist


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
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.netapp_protection_group_object_params.NetappProtectionGroupObjectParams.from_dictionary(structure))
        exclude_object_ids = dictionary.get('excludeObjectIds')
        direct_cloud_archive = dictionary.get('directCloudArchive')
        native_format = dictionary.get('nativeFormat')
        nfs_version_preference = dictionary.get('nfsVersionPreference')
        snapshot_label = cohesity_management_sdk.models_v2.snapshot_label.SnapshotLabel.from_dictionary(dictionary.get('snapshotLabel')) if dictionary.get('snapshotLabel') else None
        snap_mirror_config = cohesity_management_sdk.models_v2.snap_mirror_config.SnapMirrorConfig.from_dictionary(dictionary.get('snapMirrorConfig')) if dictionary.get('snapMirrorConfig') else None
        backup_existing_snapshot = dictionary.get('backupExistingSnapshot')
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        protocol = dictionary.get('protocol')
        continue_on_error = dictionary.get('continueOnError')
        continuous_snapshots = cohesity_management_sdk.models_v2.continuous_snapshot_params.ContinuousSnapshotParams.from_dictionary(dictionary.get('continuousSnapshots')) if dictionary.get('continuousSnapshots') else None
        encryption_enabled = dictionary.get('encryptionEnabled')
        file_lock_config = cohesity_management_sdk.models_v2.file_level_data_lock_configurations.FileLevelDataLockConfigurations.from_dictionary(dictionary.get('fileLockConfig')) if dictionary.get('fileLockConfig') else None
        file_filters = cohesity_management_sdk.models_v2.protection_group_file_filtering_policy.ProtectionGroupFileFilteringPolicy.from_dictionary(dictionary.get('fileFilters')) if dictionary.get('fileFilters') else None
        filter_ip_config = cohesity_management_sdk.models_v2.filter_ip_configuration.FilterIPConfiguration.from_dictionary(dictionary.get('filterIpConfig')) if dictionary.get('filterIpConfig') else None
        modify_source_permissions = dictionary.get('modifySourcePermissions')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        pre_post_script = cohesity_management_sdk.models_v2.host_based_backup_script_params.HostBasedBackupScriptParams.from_dictionary(dictionary.get('prePostScript')) if dictionary.get('prePostScript') else None
        throttling_config = cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration.NasSourceAndProtectionThrottlingConfiguration.from_dictionary(dictionary.get('throttlingConfig')) if dictionary.get('throttlingConfig') else None
        use_changelist = dictionary.get('useChangelist')

        # Return an object of this model
        return cls(objects,
                   exclude_object_ids,
                   direct_cloud_archive,
                   native_format,
                   nfs_version_preference,
                   snapshot_label,
                   snap_mirror_config,
                   backup_existing_snapshot,
                   indexing_policy,
                   protocol,
                   continue_on_error,
                   continuous_snapshots,
                   encryption_enabled,
                   file_lock_config,
                   file_filters,
                   filter_ip_config,
                   modify_source_permissions,
                   source_id,
                   source_name,
                   pre_post_script,
                   throttling_config,
                   use_changelist)