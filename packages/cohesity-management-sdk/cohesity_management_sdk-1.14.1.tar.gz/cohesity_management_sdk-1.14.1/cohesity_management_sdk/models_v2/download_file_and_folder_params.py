# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_file_and_folder_info

class DownloadFileAndFolderParams(object):

    """Implementation of the 'Download File And Folder Params' model.

    Specifies the parameters to download files and folders.

    Attributes:
        files_and_folders (list of CommonFileAndFolderInfo): Specifies the
            info about the files and folders to be recovered.
        download_file_path (string): Specifies the path location to download
            the files and folders.
        expiry_time_usecs (long|int): Specifies the time upto which the download link is available.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "files_and_folders":'filesAndFolders',
        "download_file_path":'downloadFilePath',
        "expiry_time_usecs":'expiryTimeUsecs'
    }

    def __init__(self,
                 files_and_folders=None,
                 download_file_path=None,
                 expiry_time_usecs=None):
        """Constructor for the DownloadFileAndFolderParams class"""

        # Initialize members of the class
        self.files_and_folders = files_and_folders
        self.download_file_path = download_file_path
        self.expiry_time_usecs = expiry_time_usecs


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
        files_and_folders = None
        if dictionary.get("filesAndFolders") is not None:
            files_and_folders = list()
            for structure in dictionary.get('filesAndFolders'):
                files_and_folders.append(cohesity_management_sdk.models_v2.common_file_and_folder_info.CommonFileAndFolderInfo.from_dictionary(structure))
        download_file_path = dictionary.get('downloadFilePath')
        expiry_time_usecs = dictionary.get('expiryTimeUsecs')

        # Return an object of this model
        return cls(files_and_folders,
                   download_file_path,
                   expiry_time_usecs)