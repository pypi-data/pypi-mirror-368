# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.recover_nas_volume_params_2
import cohesity_management_sdk.models_v2.recover_file_and_folder_params_6
import cohesity_management_sdk.models_v2.download_file_and_folder_params

class RecoverIsilonParams(object):

    """Implementation of the 'Recover Isilon Params.' model.

    Specifies the recovery options specific to Isilon environment.

    Attributes:
        objects (list of CommonRecoverObjectSnapshotParams): Specifies the
            list of recover Object parameters.
        recovery_action (RecoveryAction5Enum): Specifies the type of recover
            action to be performed.
        recover_nas_volume_params (RecoverNasVolumeParams2): Specifies the
            parameters to recover NAS Volumes.
        recover_file_and_folder_params (RecoverFileAndFolderParams6):
            Specifies the parameters to recover files.
        download_file_and_folder_params (DownloadFileAndFolderParams):
            Specifies the parameters to download files and folders.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "recovery_action":'recoveryAction',
        "recover_nas_volume_params":'recoverNasVolumeParams',
        "recover_file_and_folder_params":'recoverFileAndFolderParams',
        "download_file_and_folder_params":'downloadFileAndFolderParams'
    }

    def __init__(self,
                 objects=None,
                 recovery_action=None,
                 recover_nas_volume_params=None,
                 recover_file_and_folder_params=None,
                 download_file_and_folder_params=None):
        """Constructor for the RecoverIsilonParams class"""

        # Initialize members of the class
        self.objects = objects
        self.recovery_action = recovery_action
        self.recover_nas_volume_params = recover_nas_volume_params
        self.recover_file_and_folder_params = recover_file_and_folder_params
        self.download_file_and_folder_params = download_file_and_folder_params


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
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(structure))
        recovery_action = dictionary.get('recoveryAction')
        recover_nas_volume_params = cohesity_management_sdk.models_v2.recover_nas_volume_params_2.RecoverNasVolumeParams2.from_dictionary(dictionary.get('recoverNasVolumeParams')) if dictionary.get('recoverNasVolumeParams') else None
        recover_file_and_folder_params = cohesity_management_sdk.models_v2.recover_file_and_folder_params_6.RecoverFileAndFolderParams6.from_dictionary(dictionary.get('recoverFileAndFolderParams')) if dictionary.get('recoverFileAndFolderParams') else None
        download_file_and_folder_params = cohesity_management_sdk.models_v2.download_file_and_folder_params.DownloadFileAndFolderParams.from_dictionary(dictionary.get('downloadFileAndFolderParams')) if dictionary.get('downloadFileAndFolderParams') else None

        # Return an object of this model
        return cls(objects,
                   recovery_action,
                   recover_nas_volume_params,
                   recover_file_and_folder_params,
                   download_file_and_folder_params)


