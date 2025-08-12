# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class ThrottlingPolicy_StorageArraySnapshotMaxSpaceConfig(object):

    """Implementation of the 'ThrottlingPolicy_StorageArraySnapshotMaxSpaceConfig' model.

    Attributes:
        max_snapshot_space_percentage (int): Max space threshold can used by
            snapshots in percentage in volume/lun to take storage snapshot. If
            the space used by snapshots in a volume/lun exceeds this threshold,
            snapshots should not be taken
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "max_snapshot_space_percentage":'maxSnapshotSpacePercentage'
    }

    def __init__(self,
                 max_snapshot_space_percentage=None):
        """Constructor for the ThrottlingPolicy_StorageArraySnapshotMaxSpaceConfig class"""

        # Initialize members of the class
        self.max_snapshot_space_percentage = max_snapshot_space_percentage


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
        max_snapshot_space_percentage = dictionary.get('maxSnapshotSpacePercentage')

        # Return an object of this model
        return cls(max_snapshot_space_percentage)
