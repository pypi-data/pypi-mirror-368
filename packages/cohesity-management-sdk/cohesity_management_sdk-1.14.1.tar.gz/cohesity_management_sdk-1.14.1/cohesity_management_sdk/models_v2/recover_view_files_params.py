# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models_v2.view_recover_file_and_folder_info
import cohesity_management_sdk.models_v2.recover_view_to_view_files_target_params

class RecoverViewFilesParams(object):
    """Implementation of the 'RecoverViewFilesParams' model.

    Specifies the parameters to recover View files.

    Attributes:
        files_and_folders (list of ViewRecoverFileAndFolderInfo): Specifies the list of info about the view files and folders to be recovered.
        view_target_params (RecoverViewToViewFilesTargetParams): Specifies configuration of the target view to which the files and folders are to be recovered.
    """

    _names = {
        "files_and_folders":"filesAndFolders",
        "view_target_params":"viewTargetParams",
    }

    def __init__(self,
                 files_and_folders=None,
                 view_target_params=None):
        """Constructor for the RecoverViewFilesParams class"""

        self.files_and_folders = files_and_folders
        self.view_target_params = view_target_params


    @classmethod
    def from_dictionary(cls, dictionary):
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

        files_and_folders = None
        if dictionary.get('filesAndFolders') is not None:
            files_and_folders = list()
            for structure in dictionary.get('filesAndFolders'):
                files_and_folders.append(cohesity_management_sdk.models_v2.view_recover_file_and_folder_info.ViewRecoverFileAndFolderInfo.from_dictionary(structure))
        view_target_params = cohesity_management_sdk.models_v2.recover_view_to_view_files_target_params.RecoverViewToViewFilesTargetParams.from_dictionary(dictionary.get('viewTargetParams')) if dictionary.get('viewTargetParams') else None

        return cls(
            files_and_folders,
            view_target_params
        )