# -*- coding: utf-8 -*-


class StorageSnapshotMgmtMaxSpaceConfig(object):

    """Implementation of the 'Storage Snapshot Mgmt Max Space Config' model.

    Specifies max space threshold configuration that can used by snapshots
      to take storage snapshot.

    Attributes:
        max_snapshot_space_percentage (long|int): Specifies max space threshold can used by snapshots in percentage
          in volume/lun to take storage snapshot.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "max_snapshot_space_percentage":'maxSnapshotSpacePercentage'
    }

    def __init__(self,
                 max_snapshot_space_percentage=None):
        """Constructor for the StorageSnapshotMgmtMaxSpaceConfig class"""

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