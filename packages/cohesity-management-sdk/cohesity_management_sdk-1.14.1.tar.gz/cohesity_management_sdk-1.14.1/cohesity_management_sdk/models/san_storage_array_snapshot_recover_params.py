# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class SANStorageArraySnapshotRecoverParams(object):

    """Implementation of the 'SANStorageArraySnapshotRecoverParams' model.

    This message contains information about SAN storage arrays snapshot
    recovery

    Attributes:
        storage_array_snapshot_id (string): TODO: Type desctiption here.
        storage_array_snapshot_name (string): TODO: Type desctiption here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "storage_array_snapshot_id": 'storageArraySnapshotId',
        "storage_array_snapshot_name": 'storageArraySnapshotName'
    }

    def __init__(self,
                 storage_array_snapshot_id=None,
                 storage_array_snapshot_name=None):
        """Constructor for the SANStorageArraySnapshotRecoverParams class"""

        # Initialize members of the class
        self.storage_array_snapshot_id = storage_array_snapshot_id
        self.storage_array_snapshot_name = storage_array_snapshot_name


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
        storage_array_snapshot_id = dictionary.get('storageArraySnapshotId', None)
        storage_array_snapshot_name = dictionary.get('storageArraySnapshotName', None)

        # Return an object of this model
        return cls(storage_array_snapshot_id,
                   storage_array_snapshot_name)


