# -*- coding: utf-8 -*-


class ProgressStats(object):

    """Implementation of the 'ProgressStats' model.

    Specifies the stats within progress.

    Attributes:
        file_walk_done (bool): Specifies whether the file system walk is done.
            Only applicable to file based backups.
        total_file_count (long|int): Specifies the total number of file and
            directory entities visited in this backup. Only applicable to file
            based backups.
        backup_file_count (long|int): Specifies the total number of file and
            directory entities that are backed up in this run. Only applicable
            to file based backups.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "file_walk_done":'fileWalkDone',
        "total_file_count":'totalFileCount',
        "backup_file_count":'backupFileCount'
    }

    def __init__(self,
                 file_walk_done=None,
                 total_file_count=None,
                 backup_file_count=None):
        """Constructor for the ProgressStats class"""

        # Initialize members of the class
        self.file_walk_done = file_walk_done
        self.total_file_count = total_file_count
        self.backup_file_count = backup_file_count


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
        file_walk_done = dictionary.get('fileWalkDone')
        total_file_count = dictionary.get('totalFileCount')
        backup_file_count = dictionary.get('backupFileCount')

        # Return an object of this model
        return cls(file_walk_done,
                   total_file_count,
                   backup_file_count)


