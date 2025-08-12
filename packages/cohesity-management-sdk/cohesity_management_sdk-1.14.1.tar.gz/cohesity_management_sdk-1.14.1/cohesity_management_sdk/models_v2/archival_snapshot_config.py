# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.archival_target_configuration_1
import cohesity_management_sdk.models_v2.update_archival_snapshot_config

class ArchivalSnapshotConfig(object):

    """Implementation of the 'Archival Snapshot Config.' model.

    Specifies the params to perform actions on archival snapshots taken by a
    Protection Group Run.

    Attributes:
        new_snapshot_config (list of ArchivalTargetConfiguration1): Specifies
            the new configuration about adding Archival Snapshot to existing
            Protection Group Run.
        update_existing_snapshot_config (list of
            UpdateArchivalSnapshotConfig): Specifies the configuration about
            updating an existing Archival Snapshot Run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "new_snapshot_config":'newSnapshotConfig',
        "update_existing_snapshot_config":'updateExistingSnapshotConfig'
    }

    def __init__(self,
                 new_snapshot_config=None,
                 update_existing_snapshot_config=None):
        """Constructor for the ArchivalSnapshotConfig class"""

        # Initialize members of the class
        self.new_snapshot_config = new_snapshot_config
        self.update_existing_snapshot_config = update_existing_snapshot_config


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
        new_snapshot_config = None
        if dictionary.get("newSnapshotConfig") is not None:
            new_snapshot_config = list()
            for structure in dictionary.get('newSnapshotConfig'):
                new_snapshot_config.append(cohesity_management_sdk.models_v2.archival_target_configuration_1.ArchivalTargetConfiguration1.from_dictionary(structure))
        update_existing_snapshot_config = None
        if dictionary.get("updateExistingSnapshotConfig") is not None:
            update_existing_snapshot_config = list()
            for structure in dictionary.get('updateExistingSnapshotConfig'):
                update_existing_snapshot_config.append(cohesity_management_sdk.models_v2.update_archival_snapshot_config.UpdateArchivalSnapshotConfig.from_dictionary(structure))

        # Return an object of this model
        return cls(new_snapshot_config,
                   update_existing_snapshot_config)


