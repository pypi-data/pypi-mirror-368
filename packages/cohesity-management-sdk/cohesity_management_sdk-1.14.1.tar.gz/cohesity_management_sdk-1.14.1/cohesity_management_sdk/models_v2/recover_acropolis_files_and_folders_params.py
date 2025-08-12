# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_file_and_folder_info
import cohesity_management_sdk.models_v2.acropolis_target_params_2

class RecoverAcropolisFilesAndFoldersParams(object):

    """Implementation of the 'Recover Acropolis Files and Folders Params.' model.

    Specifies the parameters to recover Acropolis files and folders.

    Attributes:
        files_and_folders (list of CommonFileAndFolderInfo): Specifies the
            info about the files and folders to be recovered.
        target_environment (string): Specifies the environment of the recovery
            target. The corresponding params below must be filled out.
        acropolis_target_params (AcropolisTargetParams2): Specifies the params
            for recovering to an Acropolis target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "files_and_folders":'filesAndFolders',
        "target_environment":'targetEnvironment',
        "acropolis_target_params":'acropolisTargetParams'
    }

    def __init__(self,
                 files_and_folders=None,
                 target_environment='kAcropolis',
                 acropolis_target_params=None):
        """Constructor for the RecoverAcropolisFilesAndFoldersParams class"""

        # Initialize members of the class
        self.files_and_folders = files_and_folders
        self.target_environment = target_environment
        self.acropolis_target_params = acropolis_target_params


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
        target_environment = dictionary.get("targetEnvironment") if dictionary.get("targetEnvironment") else 'kAcropolis'
        acropolis_target_params = cohesity_management_sdk.models_v2.acropolis_target_params_2.AcropolisTargetParams2.from_dictionary(dictionary.get('acropolisTargetParams')) if dictionary.get('acropolisTargetParams') else None

        # Return an object of this model
        return cls(files_and_folders,
                   target_environment,
                   acropolis_target_params)


