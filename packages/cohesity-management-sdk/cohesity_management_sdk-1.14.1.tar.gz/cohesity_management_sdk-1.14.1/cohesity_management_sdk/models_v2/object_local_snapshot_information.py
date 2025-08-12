# -*- coding: utf-8 -*-


class ObjectLocalSnapshotInformation(object):

    """Implementation of the 'Object Local Snapshot Information.' model.

    Specifies the Local snapshot information for the object.

    Attributes:
        snapshot_id (string): Specifies the id of the local snapshot for the
            object.
        logical_size_bytes (long|int): Specifies the logical size of this
            snapshot in bytes.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "snapshot_id":'snapshotId',
        "logical_size_bytes":'logicalSizeBytes'
    }

    def __init__(self,
                 snapshot_id=None,
                 logical_size_bytes=None):
        """Constructor for the ObjectLocalSnapshotInformation class"""

        # Initialize members of the class
        self.snapshot_id = snapshot_id
        self.logical_size_bytes = logical_size_bytes


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
        snapshot_id = dictionary.get('snapshotId')
        logical_size_bytes = dictionary.get('logicalSizeBytes')

        # Return an object of this model
        return cls(snapshot_id,
                   logical_size_bytes)


