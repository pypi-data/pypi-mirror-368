# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.download_file_and_folder_params
import cohesity_management_sdk.models_v2.recover_view_files_params

class RecoverViewEnvironmentParams(object):

    """Implementation of the 'Recover View environment params.' model.

    Specifies the recovery options specific to View environment.

    Attributes:
        objects (list of CommonRecoverObjectSnapshotParams): Specifies the
            list of recover Object parameters.
        recovery_action (string): Specifies the type of recovery action to be
            performed.
        download_file_and_folder_params (DownloadFileAndFolderParams):
            Specifies the parameters to download files and folders.
        recover_file_and_folder_params (RecoverViewFilesParams): Specifies the parameters to recover files.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_action":'recoveryAction',
        "objects":'objects',
        "download_file_and_folder_params":'downloadFileAndFolderParams',
        "recover_file_and_folder_params":'recoverFileAndFolderParams'
    }

    def __init__(self,
                 recovery_action='DownloadFilesAndFolders',
                 objects=None,
                 download_file_and_folder_params=None,
                 recover_file_and_folder_params=None):
        """Constructor for the RecoverViewEnvironmentParams class"""

        # Initialize members of the class
        self.objects = objects
        self.recovery_action = recovery_action
        self.download_file_and_folder_params = download_file_and_folder_params
        self.recover_file_and_folder_params = recover_file_and_folder_params


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
        recovery_action = dictionary.get("recoveryAction")
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(structure))
        download_file_and_folder_params = cohesity_management_sdk.models_v2.download_file_and_folder_params.DownloadFileAndFolderParams.from_dictionary(dictionary.get('downloadFileAndFolderParams')) if dictionary.get('downloadFileAndFolderParams') else None
        recover_file_and_folder_params = cohesity_management_sdk.models_v2.recover_view_files_params.RecoverViewFilesParams.from_dictionary(
            dictionary.get('recoverFileAndFolderParams')) if dictionary.get('recoverFileAndFolderParams') else None

        # Return an object of this model
        return cls(recovery_action,
                   objects,
                   download_file_and_folder_params,
                   recover_file_and_folder_params)