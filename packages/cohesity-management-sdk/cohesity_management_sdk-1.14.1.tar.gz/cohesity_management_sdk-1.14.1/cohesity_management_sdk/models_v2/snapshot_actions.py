# -*- coding: utf-8 -*-


class SnapshotActions(object):

    """Implementation of the 'Snapshot Actions' model.

    Snapshot Actions

    Attributes:
        snapshot_actions (SnapshotActions1Enum): Snapshot Actions

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "snapshot_actions":'snapshotActions'
    }

    def __init__(self,
                 snapshot_actions=None):
        """Constructor for the SnapshotActions class"""

        # Initialize members of the class
        self.snapshot_actions = snapshot_actions


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
        snapshot_actions = dictionary.get('snapshotActions')

        # Return an object of this model
        return cls(snapshot_actions)


