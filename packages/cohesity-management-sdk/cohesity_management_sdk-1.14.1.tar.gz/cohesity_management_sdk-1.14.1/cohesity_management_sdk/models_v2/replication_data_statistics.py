# -*- coding: utf-8 -*-


class ReplicationDataStatistics(object):

    """Implementation of the 'Replication data statistics.' model.

    Specifies statistics about replication data.

    Attributes:
        logical_size_bytes (long|int): Specifies the total logical size in
            bytes.
        logical_bytes_transferred (long|int): Specifies the total logical
            bytes transferred.
        physical_bytes_transferred (long|int): Specifies the total physical
            bytes transferred.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "logical_size_bytes":'logicalSizeBytes',
        "logical_bytes_transferred":'logicalBytesTransferred',
        "physical_bytes_transferred":'physicalBytesTransferred'
    }

    def __init__(self,
                 logical_size_bytes=None,
                 logical_bytes_transferred=None,
                 physical_bytes_transferred=None):
        """Constructor for the ReplicationDataStatistics class"""

        # Initialize members of the class
        self.logical_size_bytes = logical_size_bytes
        self.logical_bytes_transferred = logical_bytes_transferred
        self.physical_bytes_transferred = physical_bytes_transferred


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
        logical_size_bytes = dictionary.get('logicalSizeBytes')
        logical_bytes_transferred = dictionary.get('logicalBytesTransferred')
        physical_bytes_transferred = dictionary.get('physicalBytesTransferred')

        # Return an object of this model
        return cls(logical_size_bytes,
                   logical_bytes_transferred,
                   physical_bytes_transferred)


