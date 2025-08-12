# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.nas_full_backup_throttling_params
import cohesity_management_sdk.models_v2.nas_full_backup_throttling_params_1

class NasSourceAndProtectionThrottlingConfiguration(object):

    """Implementation of the 'Nas Source and Protection Throttling Configuration' model.

    Specifies the source throttling parameters to be used during full or
    incremental backup of the NAS source.

    Attributes:
        full_backup_config (NASFullBackupThrottlingParams): Specifies the
            throttling configuration during full backup run.
        incremental_backup_config (NASFullBackupThrottlingParams1): TODO: type
            description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "full_backup_config":'fullBackupConfig',
        "incremental_backup_config":'incrementalBackupConfig'
    }

    def __init__(self,
                 full_backup_config=None,
                 incremental_backup_config=None):
        """Constructor for the NasSourceAndProtectionThrottlingConfiguration class"""

        # Initialize members of the class
        self.full_backup_config = full_backup_config
        self.incremental_backup_config = incremental_backup_config


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
        full_backup_config = cohesity_management_sdk.models_v2.nas_full_backup_throttling_params.NASFullBackupThrottlingParams.from_dictionary(dictionary.get('fullBackupConfig')) if dictionary.get('fullBackupConfig') else None
        incremental_backup_config = cohesity_management_sdk.models_v2.nas_full_backup_throttling_params_1.NASFullBackupThrottlingParams1.from_dictionary(dictionary.get('incrementalBackupConfig')) if dictionary.get('incrementalBackupConfig') else None

        # Return an object of this model
        return cls(full_backup_config,
                   incremental_backup_config)


