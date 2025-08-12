# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.file_level_data_lock_configurations
import cohesity_management_sdk.models_v2.file_filtering_policy
import cohesity_management_sdk.models_v2.host_based_backup_script_params
import cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration

class CommonNasProtectionParams(object):

    """Implementation of the 'CommonNasProtectionParams' model.

    Specifies the parameters which are specific to NAS Protection.

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

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "indexing_policy":'indexingPolicy',
        "continue_on_error":'continueOnError',
        "encryption_enabled":'encryptionEnabled',
        "file_lock_config":'fileLockConfig',
        "file_filters":'fileFilters',
        "pre_post_script":'prePostScript',
        "throttling_config":'throttlingConfig'
    }

    def __init__(self,
                 indexing_policy=None,
                 continue_on_error=None,
                 encryption_enabled=None,
                 file_lock_config=None,
                 file_filters=None,
                 pre_post_script=None,
                 throttling_config=None):
        """Constructor for the CommonNasProtectionParams class"""

        # Initialize members of the class
        self.indexing_policy = indexing_policy
        self.continue_on_error = continue_on_error
        self.encryption_enabled = encryption_enabled
        self.file_lock_config = file_lock_config
        self.file_filters = file_filters
        self.pre_post_script = pre_post_script
        self.throttling_config = throttling_config


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

        # Return an object of this model
        return cls(indexing_policy,
                   continue_on_error,
                   encryption_enabled,
                   file_lock_config,
                   file_filters,
                   pre_post_script,
                   throttling_config)


