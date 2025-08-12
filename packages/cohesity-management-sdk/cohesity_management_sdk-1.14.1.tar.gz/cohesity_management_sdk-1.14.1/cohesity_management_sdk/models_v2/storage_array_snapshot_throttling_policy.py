# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.storage_snapshot_mgmt_max_snapshots_config
import cohesity_management_sdk.models_v2.storage_snapshot_mgmt_max_space_config


class StorageArraySnapshotThrottlingPolicy(object):

    """Implementation of the 'Aag Backup Preference Type.' model.

    Specifies the throttling policy for individual volume/lun.

    Attributes:
        id (long|int): Specifies the volume ID of the Storage Snapshot Mgmt throttling
          Policy.
        max_snapshots_mgmt_snapshot_config (StorageSnapshotMgmtMaxSnapshotsConfig): Specifies the max snapshots threshold configuration taken for
          storage snapshots.
        max_snapshots_config_enabled (bool): Specifies whether we will use storage snapshot managmement max
          snapshots config to all volumes/luns that are part of the registered entity.
        max_snapshots_mgmt_space_config (StorageSnapshotMgmtMaxSpaceConfig): Specifies the max space threshold configuration for storage snapshots.
        max_space_config_enabled (bool): Specifies whether we will use storage snapshot managmement max
          space config to all volumes/luns that are part of the registered entity.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'Id',
        "max_snapshots_mgmt_snapshot_config":'maxSnapshotsMgmtSnapshotConfig',
        "max_snapshots_config_enabled":'maxSnapshotsConfigEnabled',
        "max_snapshots_mgmt_space_config":'maxSnapshotsMgmtSpaceConfig',
        "max_space_config_enabled":'maxSpaceConfigEnabled',
    }

    def __init__(self,
                 id=None,
                 max_snapshots_mgmt_snapshot_config=None,
                 max_snapshots_config_enabled=None,
                 max_snapshots_mgmt_space_config=None,
                 max_space_config_enabled=None
                 ):
        """Constructor for the StorageArraySnapshotThrottlingPolicy class"""

        # Initialize members of the class
        self.id = id
        self.max_snapshots_mgmt_snapshot_config = max_snapshots_mgmt_snapshot_config
        self.max_snapshots_config_enabled = max_snapshots_config_enabled
        self.max_snapshots_mgmt_space_config = max_snapshots_mgmt_space_config
        self.max_space_config_enabled = max_space_config_enabled


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:max_snapshots_mgmt_space_config
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        id = dictionary.get('Id')
        max_snapshots_mgmt_snapshot_config = cohesity_management_sdk.models_v2.storage_snapshot_mgmt_max_snapshots_config.StorageSnapshotMgmtMaxSnapshotsConfig.from_dictionary(dictionary.get('maxSnapshotsMgmtSnapshotConfig')) if dictionary.get('maxSnapshotsMgmtSnapshotConfig') else None
        max_snapshots_config_enabled = dictionary.get('maxSnapshotsConfigEnabled')
        max_snapshots_mgmt_space_config = cohesity_management_sdk.models_v2.storage_snapshot_mgmt_max_space_config.StorageSnapshotMgmtMaxSpaceConfig.from_dictionary(
            dictionary.get('maxSnapshotsMgmtSpaceConfig')) if dictionary.get('maxSnapshotsMgmtSpaceConfig') else None
        max_space_config_enabled = dictionary.get('maxSpaceConfigEnabled')

        # Return an object of this model
        return cls(id,
                   max_snapshots_mgmt_snapshot_config,
                   max_snapshots_config_enabled,
                   max_snapshots_mgmt_space_config ,
                   max_space_config_enabled)