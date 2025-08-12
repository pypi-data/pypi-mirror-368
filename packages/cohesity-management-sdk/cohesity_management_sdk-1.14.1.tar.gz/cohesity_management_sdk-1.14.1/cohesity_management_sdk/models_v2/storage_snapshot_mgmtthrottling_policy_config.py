# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.storage_snapshot_mgmt_max_snapshots_config
import cohesity_management_sdk.models_v2.storage_snapshot_mgmt_max_space_config
import cohesity_management_sdk.models_v2.storage_array_snapshot_throttling_policy

class StorageSnapshotMgmtthrottlingPolicyConfig(object):

    """Implementation of the 'Storage Snapshot Mgmt throttling Policy Config' model.

    Specifies the max snapshots threshold configuration taken for
          storage snapshots.

    Attributes:
        max_snapshot_config (StorageSnapshotMgmtMaxSnapshotsConfig): Specifies the max snapshots threshold configuration taken for
          storage snapshots.
        max_snapshots_config_enabled (bool): Specifies whether we will use storage snapshot managmement max
          snapshots config to all volumes/luns that are part of the registered entity.
        max_space_config (StorageSnapshotMgmtMaxSpaceConfig): Specifies the max space threshold configuration for storage snapshots.
        max_space_config_enabled (bool): Specifies whether we will use storage snapshot managmement max
          space config to all volumes/luns that are part of the registered entity.
        storage_array_snapshot_throttling_policies (list of StorageArraySnapshotThrottlingPolicy): Specifies the list of storage array snapshot management throttling
          policies for individual volume/lun.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "max_snapshot_config":'maxSnapshotConfig',
        "max_snapshots_config_enabled":'maxSnapshotsConfigEnabled',
        "max_space_config":'maxSpaceConfig',
        "max_space_config_enabled":'maxSpaceConfigEnabled',
        "storage_array_snapshot_throttling_policies":'storageArraySnapshotThrottlingPolicies'
    }

    def __init__(self,
                 max_snapshot_config=None,
                 max_snapshots_config_enabled=None,
                 max_space_config=None,
                 max_space_config_enabled=None,
                 storage_array_snapshot_throttling_policies=None):
        """Constructor for the StorageSnapshotMgmtthrottlingPolicyConfig class"""

        # Initialize members of the class
        self.max_snapshot_config = max_snapshot_config
        self.max_snapshots_config_enabled = max_snapshots_config_enabled
        self.max_space_config = max_space_config
        self.max_space_config_enabled = max_space_config_enabled
        self.storage_array_snapshot_throttling_policies = storage_array_snapshot_throttling_policies


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
        max_snapshot_config = cohesity_management_sdk.models_v2.storage_snapshot_mgmt_max_snapshots_config.StorageSnapshotMgmtMaxSnapshotsConfig.from_dictionary(
            dictionary.get('maxSnapshotConfig')) if dictionary.get('maxSnapshotConfig') else None
        max_snapshots_config_enabled = dictionary.get('maxSnapshotsConfigEnabled')
        max_space_config  = cohesity_management_sdk.models_v2.storage_snapshot_mgmt_max_space_config.StorageSnapshotMgmtMaxSpaceConfig.from_dictionary(
            dictionary.get('maxSpaceConfig')) if dictionary.get('maxSpaceConfig') else None
        max_space_config_enabled = dictionary.get('maxSpaceConfigEnabled')
        storage_array_snapshot_throttling_policies = None
        if dictionary.get('storageArraySnapshotThrottlingPolicies') is not None:
            storage_array_snapshot_throttling_policies = list()
            for structure in dictionary.get('storageArraySnapshotThrottlingPolicies'):
                storage_array_snapshot_throttling_policies.append(cohesity_management_sdk.models_v2.storage_array_snapshot_throttling_policy.StorageArraySnapshotThrottlingPolicy.from_dictionary(structure))



        # Return an object of this model
        return cls(max_snapshot_config,
                   max_snapshots_config_enabled,
                   max_space_config,
                   max_space_config_enabled,
                   storage_array_snapshot_throttling_policies)