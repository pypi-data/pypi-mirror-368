# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_file_and_folder_info
import cohesity_management_sdk.models_v2.physical_target_params_2

class RecoverPhysicalFileAndFolderParams(object):

    """Implementation of the 'Recover Physical File And Folder Params' model.

    Specifies the parameters to recover files and folders.

    Attributes:
        files_and_folders (list of CommonFileAndFolderInfo): Specifies the
            information about the files and folders to be recovered.
        target_environment (string): Specifies the environment of the recovery
            target. The corresponding params below must be filled out.
        physical_target_params (PhysicalTargetParams2): Specifies the
            parameters to recover to a Physical target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "files_and_folders":'filesAndFolders',
        "target_environment":'targetEnvironment',
        "physical_target_params":'physicalTargetParams'
    }

    def __init__(self,
                 files_and_folders=None,
                 target_environment='kPhysical',
                 physical_target_params=None):
        """Constructor for the RecoverPhysicalFileAndFolderParams class"""

        # Initialize members of the class
        self.files_and_folders = files_and_folders
        self.target_environment = target_environment
        self.physical_target_params = physical_target_params


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
        target_environment = dictionary.get("targetEnvironment") if dictionary.get("targetEnvironment") else 'kPhysical'
        physical_target_params = cohesity_management_sdk.models_v2.physical_target_params_2.PhysicalTargetParams2.from_dictionary(dictionary.get('physicalTargetParams')) if dictionary.get('physicalTargetParams') else None

        # Return an object of this model
        return cls(files_and_folders,
                   target_environment,
                   physical_target_params)


