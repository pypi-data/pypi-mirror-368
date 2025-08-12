# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.files_and_folders_object

class DownloadFilesAndFoldersRecoveryParams1(object):

    """Implementation of the 'Download Files And Folders Recovery Params.1' model.

    Specifies the parameters to create a download files and folders Recovery.

    Attributes:
        name (string): Specifies the name of the recovery task. This field
            must be set and must be a unique name.
        object (CommonRecoverObjectSnapshotParams): Specifies the common
            snapshot parameters for a protected object.
        files_and_folders (list of FilesAndFoldersObject): Specifies the list
            of files and folders to download.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "object":'object',
        "files_and_folders":'filesAndFolders'
    }

    def __init__(self,
                 name=None,
                 object=None,
                 files_and_folders=None):
        """Constructor for the DownloadFilesAndFoldersRecoveryParams1 class"""

        # Initialize members of the class
        self.name = name
        self.object = object
        self.files_and_folders = files_and_folders


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
        name = dictionary.get('name')
        object = cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(dictionary.get('object')) if dictionary.get('object') else None
        files_and_folders = None
        if dictionary.get("filesAndFolders") is not None:
            files_and_folders = list()
            for structure in dictionary.get('filesAndFolders'):
                files_and_folders.append(cohesity_management_sdk.models_v2.files_and_folders_object.FilesAndFoldersObject.from_dictionary(structure))

        # Return an object of this model
        return cls(name,
                   object,
                   files_and_folders)


