# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.file_level_data_lock_configurations
import cohesity_management_sdk.models_v2.file_filtering_policy
import cohesity_management_sdk.models_v2.host_based_backup_script_params
import cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration
import cohesity_management_sdk.models_v2.snapshot_label
import cohesity_management_sdk.models_v2.continuous_snapshot_params

class NetappObjectProtectionResponseParams(object):

    """Implementation of the 'NetappObjectProtectionResponseParams' model.

    Specifies the parameters which are specific to Netapp object protection.

    Attributes:
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        continue_on_error (bool): Specifies whether or not the backup should
            continue regardless of whether or not an error was encountered.
        encryption_enabled (bool): Specifies whether the encryption should be
            used while backup or not.
        file_lock_config (FileLevelDataLockConfigurations): Specifies a config
            to lock files in a view - to protect from malicious or an
            accidental attempt to delete or modify the files in this view.
        file_filters (FileFilteringPolicy): Specifies a set of filters for a
            file based Protection Group. These values are strings which can
            represent a prefix or suffix. Example: '/tmp' or '*.mp4'. For file
            based Protection Groups, all files under prefixes specified by the
            'includeFilters' list will be protected unless they are explicitly
            excluded by the 'excludeFilters' list.
        pre_post_script (HostBasedBackupScriptParams): Specifies params of a
            pre/post scripts to be executed before and after a backup run.
        throttling_config (NasSourceAndProtectionThrottlingConfiguration):
            Specifies the source throttling parameters to be used during full
            or incremental backup of the NAS source.
        protocol (Protocol4Enum): Specifies the protocol of the NAS device
            being backed up.
        exclude_object_ids (list of long|int): Specifies the objects to be
            excluded in the Protection.
        snapshot_label (SnapshotLabel): Specifies the snapshot label for
            incremental and full backup of Secondary Netapp volumes
            (Data-Protect Volumes).
        backup_existing_snapshot (bool): Specifies that snapshot label is not
            set for Data-Protect Netapp Volumes backup. If field is set to
            true, existing oldest snapshot is used for backup and subsequent
            incremental will be selected in ascending order of snapshot create
            time on the source. If snapshot label is set, this field is set to
            false.
        continuous_snapshots (ContinuousSnapshotParams): Specifies the source
            snapshots to be taken even if there is a pending run in a
            protection group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "indexing_policy":'indexingPolicy',
        "continue_on_error":'continueOnError',
        "encryption_enabled":'encryptionEnabled',
        "file_lock_config":'fileLockConfig',
        "file_filters":'fileFilters',
        "pre_post_script":'prePostScript',
        "throttling_config":'throttlingConfig',
        "protocol":'protocol',
        "exclude_object_ids":'excludeObjectIds',
        "snapshot_label":'snapshotLabel',
        "backup_existing_snapshot":'backupExistingSnapshot',
        "continuous_snapshots":'continuousSnapshots'
    }

    def __init__(self,
                 indexing_policy=None,
                 continue_on_error=None,
                 encryption_enabled=None,
                 file_lock_config=None,
                 file_filters=None,
                 pre_post_script=None,
                 throttling_config=None,
                 protocol=None,
                 exclude_object_ids=None,
                 snapshot_label=None,
                 backup_existing_snapshot=None,
                 continuous_snapshots=None):
        """Constructor for the NetappObjectProtectionResponseParams class"""

        # Initialize members of the class
        self.indexing_policy = indexing_policy
        self.continue_on_error = continue_on_error
        self.encryption_enabled = encryption_enabled
        self.file_lock_config = file_lock_config
        self.file_filters = file_filters
        self.pre_post_script = pre_post_script
        self.throttling_config = throttling_config
        self.protocol = protocol
        self.exclude_object_ids = exclude_object_ids
        self.snapshot_label = snapshot_label
        self.backup_existing_snapshot = backup_existing_snapshot
        self.continuous_snapshots = continuous_snapshots


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
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        continue_on_error = dictionary.get('continueOnError')
        encryption_enabled = dictionary.get('encryptionEnabled')
        file_lock_config = cohesity_management_sdk.models_v2.file_level_data_lock_configurations.FileLevelDataLockConfigurations.from_dictionary(dictionary.get('fileLockConfig')) if dictionary.get('fileLockConfig') else None
        file_filters = cohesity_management_sdk.models_v2.file_filtering_policy.FileFilteringPolicy.from_dictionary(dictionary.get('fileFilters')) if dictionary.get('fileFilters') else None
        pre_post_script = cohesity_management_sdk.models_v2.host_based_backup_script_params.HostBasedBackupScriptParams.from_dictionary(dictionary.get('prePostScript')) if dictionary.get('prePostScript') else None
        throttling_config = cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration.NasSourceAndProtectionThrottlingConfiguration.from_dictionary(dictionary.get('throttlingConfig')) if dictionary.get('throttlingConfig') else None
        protocol = dictionary.get('protocol')
        exclude_object_ids = dictionary.get('excludeObjectIds')
        snapshot_label = cohesity_management_sdk.models_v2.snapshot_label.SnapshotLabel.from_dictionary(dictionary.get('snapshotLabel')) if dictionary.get('snapshotLabel') else None
        backup_existing_snapshot = dictionary.get('backupExistingSnapshot')
        continuous_snapshots = cohesity_management_sdk.models_v2.continuous_snapshot_params.ContinuousSnapshotParams.from_dictionary(dictionary.get('continuousSnapshots')) if dictionary.get('continuousSnapshots') else None

        # Return an object of this model
        return cls(indexing_policy,
                   continue_on_error,
                   encryption_enabled,
                   file_lock_config,
                   file_filters,
                   pre_post_script,
                   throttling_config,
                   protocol,
                   exclude_object_ids,
                   snapshot_label,
                   backup_existing_snapshot,
                   continuous_snapshots)


