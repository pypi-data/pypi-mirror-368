# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class SnapshotFolderCounts(object):

    """Implementation of the 'SnapshotFolderCounts' model.

    Represents the count of folders associated with different roots during the
      backup process.

    Attributes:
        backed_up_folder_count (int): Total count of folders
          that are backed up for given root during backup.
        folder_root_type (int): The root folder of the current folder.
        skipped_folder_count (int): Total count of folders that are skipped for given root during
          backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "backed_up_folder_count":'backedUpFolderCount',
        "folder_root_type":'folderRootType',
        "skipped_folder_count":'skippedFolderCount'
    }

    def __init__(self,
                 backed_up_folder_count=None,
                 folder_root_type=None,
                 skipped_folder_count=None):
        """Constructor for the SnapshotFolderCounts class"""

        # Initialize members of the class
        self.backed_up_folder_count = backed_up_folder_count
        self.folder_root_type = folder_root_type
        self.skipped_folder_count = skipped_folder_count


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
        backed_up_folder_count = dictionary.get('backedUpFolderCount')
        folder_root_type = dictionary.get('folderRootType')
        skipped_folder_count = dictionary.get('skippedFolderCount')

        # Return an object of this model
        return cls(backed_up_folder_count,
                   folder_root_type,
                   skipped_folder_count)