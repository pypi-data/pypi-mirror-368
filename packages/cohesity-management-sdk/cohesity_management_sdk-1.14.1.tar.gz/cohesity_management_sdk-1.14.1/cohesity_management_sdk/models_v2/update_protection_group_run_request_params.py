# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.local_snapshot_config
import cohesity_management_sdk.models_v2.replication_snapshot_config
import cohesity_management_sdk.models_v2.archival_snapshot_config

class UpdateProtectionGroupRunRequestParams(object):

    """Implementation of the 'Update Protection Group Run Request Params.' model.

    Specifies the params to update a Protection Group Run.

    Attributes:
        run_id (string): Specifies a unique Protection Group Run id.
        local_snapshot_config (LocalSnapshotConfig): Specifies the params to
            perform actions on local snapshot taken by a Protection Group
            Run.
        replication_snapshot_config (ReplicationSnapshotConfig): Specifies the
            params to perform actions on replication snapshots taken by a
            Protection Group Run.
        archival_snapshot_config (ArchivalSnapshotConfig): Specifies the
            params to perform actions on archival snapshots taken by a
            Protection Group Run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "run_id":'runId',
        "local_snapshot_config":'localSnapshotConfig',
        "replication_snapshot_config":'replicationSnapshotConfig',
        "archival_snapshot_config":'archivalSnapshotConfig'
    }

    def __init__(self,
                 run_id=None,
                 local_snapshot_config=None,
                 replication_snapshot_config=None,
                 archival_snapshot_config=None):
        """Constructor for the UpdateProtectionGroupRunRequestParams class"""

        # Initialize members of the class
        self.run_id = run_id
        self.local_snapshot_config = local_snapshot_config
        self.replication_snapshot_config = replication_snapshot_config
        self.archival_snapshot_config = archival_snapshot_config


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
        run_id = dictionary.get('runId')
        local_snapshot_config = cohesity_management_sdk.models_v2.local_snapshot_config.LocalSnapshotConfig.from_dictionary(dictionary.get('localSnapshotConfig')) if dictionary.get('localSnapshotConfig') else None
        replication_snapshot_config = cohesity_management_sdk.models_v2.replication_snapshot_config.ReplicationSnapshotConfig.from_dictionary(dictionary.get('replicationSnapshotConfig')) if dictionary.get('replicationSnapshotConfig') else None
        archival_snapshot_config = cohesity_management_sdk.models_v2.archival_snapshot_config.ArchivalSnapshotConfig.from_dictionary(dictionary.get('archivalSnapshotConfig')) if dictionary.get('archivalSnapshotConfig') else None

        # Return an object of this model
        return cls(run_id,
                   local_snapshot_config,
                   replication_snapshot_config,
                   archival_snapshot_config)


