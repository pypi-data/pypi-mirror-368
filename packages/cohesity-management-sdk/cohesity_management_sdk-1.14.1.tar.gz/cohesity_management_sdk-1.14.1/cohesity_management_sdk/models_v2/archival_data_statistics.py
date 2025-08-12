# -*- coding: utf-8 -*-


class ArchivalDataStatistics(object):

    """Implementation of the 'Archival data statistics.' model.

    Specifies statistics about archival data.

    Attributes:
        avg_logical_transfer_rate_bps (long|int): Specifies the average rate
            of transfer in bytes per second.
        backup_file_count (long|int): Specifies the total number of file and directory entities that
          are backed up in this run. Only applicable to file based backups.
        bytes_read (long|int): Specifies total logical bytes read for creating the snapshot.
        file_walk_done (bool): Specifies whether the file system walk is done. Only applicable
          to file based backups.
        logical_bytes_transferred (long|int): Specifies the logical bytes
            transferred.
        logical_size_bytes (long|int): Specifies the logicalSizeBytes.
        physical_bytes_transferred (long|int): Specifies the physical bytes
            transferred.
        total_file_count (long|int): Specifies the total number of file and directory entities visited
          in this backup. Only applicable to file based backups.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "avg_logical_transfer_rate_bps":'avgLogicalTransferRateBps',
        "backup_file_count":'backupFileCount',
        "bytes_read":'bytesRead',
        "file_walk_done":'fileWalkDone',
        "logical_size_bytes":'logicalSizeBytes',
        "logical_bytes_transferred":'logicalBytesTransferred',
        "physical_bytes_transferred":'physicalBytesTransferred',
        "total_file_count":'totalFileCount'
    }

    def __init__(self,
                 avg_logical_transfer_rate_bps=None,
                 backup_file_count=None,
                 bytes_read=None,
                 file_walk_done=None,
                 logical_size_bytes=None,
                 logical_bytes_transferred=None,
                 physical_bytes_transferred=None,
                 total_file_count=None):
        """Constructor for the ArchivalDataStatistics class"""

        # Initialize members of the class
        self.avg_logical_transfer_rate_bps = avg_logical_transfer_rate_bps
        self.backup_file_count = backup_file_count
        self.bytes_read = bytes_read
        self.file_walk_done = file_walk_done
        self.logical_size_bytes = logical_size_bytes
        self.logical_bytes_transferred = logical_bytes_transferred
        self.physical_bytes_transferred = physical_bytes_transferred
        self.total_file_count = total_file_count


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
        avg_logical_transfer_rate_bps = dictionary.get('avgLogicalTransferRateBps')
        backpup_file_count = dictionary.get('backupFileCount')
        bytes_read = dictionary.get('bytesRead')
        file_walk_done = dictionary.get('fileWalkDone')
        logical_size_bytes = dictionary.get('logicalSizeBytes')
        logical_bytes_transferred = dictionary.get('logicalBytesTransferred')
        physical_bytes_transferred = dictionary.get('physicalBytesTransferred')
        total_file_count = dictionary.get('totalFileCount')

        # Return an object of this model
        return cls(
                   avg_logical_transfer_rate_bps,
                   backpup_file_count,
                   bytes_read,
                   file_walk_done,logical_size_bytes,
                   logical_bytes_transferred,
                   physical_bytes_transferred,
                   total_file_count)