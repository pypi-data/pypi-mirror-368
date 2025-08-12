# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.root_public_folder_param
import cohesity_management_sdk.models_v2.target_root_public_folder

class RecoverPublicFoldersParams(object):

    """Implementation of the 'RecoverPublicFoldersParams' model.

    Specifies the parameters to recover Office 365 Public Folders.

    Attributes:
        root_public_folders (list of RootPublicFolderParam): Specifies a list
            of RootPublicFolder params associated with the objects to
            recover.
        target_root_public_folder (TargetRootPublicFolder): Specifies the
            target RootPublicFolder to recover to. If not specified, the
            objects will be recovered to original location.
        target_folder_path (string): Specifies the path to the target folder.
        continue_on_error (bool): Specifies whether to continue recovering
            other Public Folders if one of Public Folder failed to recover.
            Default value is false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "root_public_folders":'rootPublicFolders',
        "target_root_public_folder":'targetRootPublicFolder',
        "target_folder_path":'targetFolderPath',
        "continue_on_error":'continueOnError'
    }

    def __init__(self,
                 root_public_folders=None,
                 target_root_public_folder=None,
                 target_folder_path=None,
                 continue_on_error=None):
        """Constructor for the RecoverPublicFoldersParams class"""

        # Initialize members of the class
        self.root_public_folders = root_public_folders
        self.target_root_public_folder = target_root_public_folder
        self.target_folder_path = target_folder_path
        self.continue_on_error = continue_on_error


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
        root_public_folders = None
        if dictionary.get("rootPublicFolders") is not None:
            root_public_folders = list()
            for structure in dictionary.get('rootPublicFolders'):
                root_public_folders.append(cohesity_management_sdk.models_v2.root_public_folder_param.RootPublicFolderParam.from_dictionary(structure))
        target_root_public_folder = cohesity_management_sdk.models_v2.target_root_public_folder.TargetRootPublicFolder.from_dictionary(dictionary.get('targetRootPublicFolder')) if dictionary.get('targetRootPublicFolder') else None
        target_folder_path = dictionary.get('targetFolderPath')
        continue_on_error = dictionary.get('continueOnError')

        # Return an object of this model
        return cls(root_public_folders,
                   target_root_public_folder,
                   target_folder_path,
                   continue_on_error)


