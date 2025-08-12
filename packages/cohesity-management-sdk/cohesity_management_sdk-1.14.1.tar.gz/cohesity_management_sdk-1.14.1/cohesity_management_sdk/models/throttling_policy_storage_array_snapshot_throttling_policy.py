# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.throttling_policy_registered_source_throttling_config
import cohesity_management_sdk.models.throttling_policy_storage_array_snapshot_max_space_config
import cohesity_management_sdk.models.entity_proto

class ThrottlingPolicy_StorageArraySnapshotThrottlingPolicy(object):

    """Implementation of the 'ThrottlingPolicy_StorageArraySnapshotThrottlingPolicy' model.

    Protobuf that describes the access control list (ACL) permissions for a
    bucket or for an object.

    Attributes:
        max_snapshot_config (ThrottlingPolicy_StorageArraySnapshotMaxSnapshotConfig):
            This specifies the storage array snapshot max snaps config for this
            volume/lun. Valid only when is_max_snapshots_config_enabled is true
        max_space_config (ThrottlingPolicy_StorageArraySnapshotMaxSpaceConfig):
            This specifies the storage array snapshot fre space config for this
            volume/lun. Valid only when is_max_space_config_enabled is true.'
        storage_entity (EntityProto): Volume/lun entity that the storage array
            snapshot policy apply to.
        is_max_snapshots_config_enabled (bool): If set to true, the max
            snapshots for this volume will be according to max_snapshot_config.
            If set to false, the max snapshots for this volume will be uncapped.
            If not set, there is not max snapshot override for this volume.
        is_max_space_config_enabled (bool): If set to true, the max space
            for this volume will be according to max_space_config.
            If set to false, the max space for this volume will be uncapped.
            If not set, there is not max snapshot override for this volume.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "max_snapshot_config":'maxSnapshotConfig',
        "max_space_config":'maxSpaceConfig',
        "storage_entity":'storageEntity',
        "is_max_snapshots_config_enabled":'isMaxSnapshotsConfigEnabled',
        "is_max_space_config_enabled":'isMaxSpaceConfigEnabled'
    }

    def __init__(self,
                 max_snapshot_config=None,
                 max_space_config=None,
                 storage_entity=None,
                 is_max_snapshots_config_enabled=None,
                 is_max_space_config_enabled=None):
        """Constructor for the ThrottlingPolicy_StorageArraySnapshotThrottlingPolicy class"""

        # Initialize members of the class
        self.max_snapshot_config = max_snapshot_config
        self.max_space_config = max_space_config
        self.storage_entity = storage_entity
        self.is_max_snapshots_config_enabled = is_max_snapshots_config_enabled
        self.is_max_space_config_enabled = is_max_space_config_enabled


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
        max_snapshot_config = cohesity_management_sdk.models.throttling_policy_registered_source_throttling_config.ThrottlingPolicy_StorageArraySnapshotMaxSnapshotConfig.from_dictionary(dictionary.get('maxSnapshotConfig')) if dictionary.get('maxSnapshotConfig') else None
        max_space_config = cohesity_management_sdk.models.throttling_policy_storage_array_snapshot_max_space_config.ThrottlingPolicy_StorageArraySnapshotMaxSpaceConfig.from_dictionary(dictionary.get('maxSpaceConfig')) if dictionary.get('maxSpaceConfig') else None
        storage_entity = cohesity_management_sdk.models.entity_proto.EntityProto.from_dictionary(dictionary.get('storageEntity')) if dictionary.get('storageEntity') else None
        is_max_space_config_enabled = dictionary.get('isMaxSpaceConfigEnabled')
        is_max_snapshots_config_enabled = dictionary.get('isMaxSnapshotsConfigEnabled')

        # Return an object of this model
        return cls(max_snapshot_config,
                   max_space_config,
                   storage_entity,
                   is_max_snapshots_config_enabled,
                   is_max_space_config_enabled)


