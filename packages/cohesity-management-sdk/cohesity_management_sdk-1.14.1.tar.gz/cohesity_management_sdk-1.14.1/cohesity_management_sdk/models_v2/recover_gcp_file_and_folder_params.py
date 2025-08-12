# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_file_and_folder_info
import cohesity_management_sdk.models_v2.gcp_target_params_1

class RecoverGCPFileAndFolderParams(object):

    """Implementation of the 'Recover GCP File And Folder Params' model.

    Specifies the parameters to recover files and folders.

    Attributes:
        files_and_folders (list of CommonFileAndFolderInfo): Specifies the
            info about the files and folders to be recovered.
        target_environment (string): Specifies the environment of the recovery
            target. The corresponding params below must be filled out.
        gcp_target_params (GcpTargetParams1): Specifies the parameters to
            recover to a GCP target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "files_and_folders":'filesAndFolders',
        "target_environment":'targetEnvironment',
        "gcp_target_params":'gcpTargetParams'
    }

    def __init__(self,
                 files_and_folders=None,
                 target_environment='kGCP',
                 gcp_target_params=None):
        """Constructor for the RecoverGCPFileAndFolderParams class"""

        # Initialize members of the class
        self.files_and_folders = files_and_folders
        self.target_environment = target_environment
        self.gcp_target_params = gcp_target_params


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
        target_environment = dictionary.get("targetEnvironment") if dictionary.get("targetEnvironment") else 'kGCP'
        gcp_target_params = cohesity_management_sdk.models_v2.gcp_target_params_1.GcpTargetParams1.from_dictionary(dictionary.get('gcpTargetParams')) if dictionary.get('gcpTargetParams') else None

        # Return an object of this model
        return cls(files_and_folders,
                   target_environment,
                   gcp_target_params)


