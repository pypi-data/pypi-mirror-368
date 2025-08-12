# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.replication_target_configuration
import cohesity_management_sdk.models_v2.update_replication_snapshot_config

class ReplicationSnapshotConfig(object):

    """Implementation of the 'Replication Snapshot Config.' model.

    Specifies the params to perform actions on replication snapshots taken by
    a Protection Group Run.

    Attributes:
        new_snapshot_config (list of ReplicationTargetConfiguration):
            Specifies the new configuration about adding Replication Snapshot
            to existing Protection Group Run.
        update_existing_snapshot_config (list of
            UpdateReplicationSnapshotConfig): Specifies the configuration
            about updating an existing Replication Snapshot Run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "new_snapshot_config":'newSnapshotConfig',
        "update_existing_snapshot_config":'updateExistingSnapshotConfig'
    }

    def __init__(self,
                 new_snapshot_config=None,
                 update_existing_snapshot_config=None):
        """Constructor for the ReplicationSnapshotConfig class"""

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
                new_snapshot_config.append(cohesity_management_sdk.models_v2.replication_target_configuration.ReplicationTargetConfiguration.from_dictionary(structure))
        update_existing_snapshot_config = None
        if dictionary.get("updateExistingSnapshotConfig") is not None:
            update_existing_snapshot_config = list()
            for structure in dictionary.get('updateExistingSnapshotConfig'):
                update_existing_snapshot_config.append(cohesity_management_sdk.models_v2.update_replication_snapshot_config.UpdateReplicationSnapshotConfig.from_dictionary(structure))

        # Return an object of this model
        return cls(new_snapshot_config,
                   update_existing_snapshot_config)


