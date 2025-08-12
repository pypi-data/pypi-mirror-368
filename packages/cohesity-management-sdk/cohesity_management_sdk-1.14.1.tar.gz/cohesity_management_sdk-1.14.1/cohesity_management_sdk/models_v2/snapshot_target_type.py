# -*- coding: utf-8 -*-


class SnapshotTargetType(object):

    """Implementation of the 'Snapshot Target Type' model.

    Snapshot Target Type

    Attributes:
        snapshot_target_type (SnapshotTargetType3Enum): Specifies the snapshot
            target type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "snapshot_target_type":'snapshotTargetType'
    }

    def __init__(self,
                 snapshot_target_type=None):
        """Constructor for the SnapshotTargetType class"""

        # Initialize members of the class
        self.snapshot_target_type = snapshot_target_type


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
        snapshot_target_type = dictionary.get('snapshotTargetType')

        # Return an object of this model
        return cls(snapshot_target_type)


