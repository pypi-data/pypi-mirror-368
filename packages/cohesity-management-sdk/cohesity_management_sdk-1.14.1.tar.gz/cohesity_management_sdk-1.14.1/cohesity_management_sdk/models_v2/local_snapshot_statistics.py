# -*- coding: utf-8 -*-


class LocalSnapshotStatistics(object):

    """Implementation of the 'Local snapshot statistics.' model.

    Specifies statistics about local snapshot.

    Attributes:
        logical_size_bytes (long|int): Specifies total logical size of
            object(s) in bytes.
        bytes_written (long|int): Specifies total size of data in bytes
            written after taking backup.
        bytes_read (long|int): Specifies total logical bytes read for creating
            the snapshot.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "logical_size_bytes":'logicalSizeBytes',
        "bytes_written":'bytesWritten',
        "bytes_read":'bytesRead'
    }

    def __init__(self,
                 logical_size_bytes=None,
                 bytes_written=None,
                 bytes_read=None):
        """Constructor for the LocalSnapshotStatistics class"""

        # Initialize members of the class
        self.logical_size_bytes = logical_size_bytes
        self.bytes_written = bytes_written
        self.bytes_read = bytes_read


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
        bytes_written = dictionary.get('bytesWritten')
        bytes_read = dictionary.get('bytesRead')

        # Return an object of this model
        return cls(logical_size_bytes,
                   bytes_written,
                   bytes_read)


