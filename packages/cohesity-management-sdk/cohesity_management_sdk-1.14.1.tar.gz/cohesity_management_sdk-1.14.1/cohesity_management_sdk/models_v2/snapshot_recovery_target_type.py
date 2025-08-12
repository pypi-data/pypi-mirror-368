# -*- coding: utf-8 -*-


class SnapshotRecoveryTargetType(object):

    """Implementation of the 'Snapshot Recovery Target Type' model.

    Snapshot Recovery Target Type

    Attributes:
        snapshot_recovery_target_type (string): Specifies the snapshot
            recovery target type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "snapshot_recovery_target_type":'snapshotRecoveryTargetType'
    }

    def __init__(self,
                 snapshot_recovery_target_type=None):
        """Constructor for the SnapshotRecoveryTargetType class"""

        # Initialize members of the class
        self.snapshot_recovery_target_type = snapshot_recovery_target_type


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
        snapshot_recovery_target_type = dictionary.get('snapshotRecoveryTargetType')

        # Return an object of this model
        return cls(snapshot_recovery_target_type)


