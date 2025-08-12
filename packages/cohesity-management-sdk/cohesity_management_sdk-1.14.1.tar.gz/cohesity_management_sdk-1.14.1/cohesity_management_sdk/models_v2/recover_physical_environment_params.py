# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.recover_physical_volumes_params
import cohesity_management_sdk.models_v2.mount_volume_params_1
import cohesity_management_sdk.models_v2.recover_file_and_folder_params_10
import cohesity_management_sdk.models_v2.download_file_and_folder_params
import cohesity_management_sdk.models_v2.system_recovery_params

class RecoverPhysicalEnvironmentParams(object):

    """Implementation of the 'Recover Physical environment params.' model.

    Specifies the recovery options specific to Physical environment.

    Attributes:
        objects (list of CommonRecoverObjectSnapshotParams): Specifies the
            list of Recover Object parameters. For recovering files, specifies
            the object contains the file to recover.
        recovery_action (RecoveryAction11Enum): Specifies the type of recover
            action to be performed.
        recover_volume_params (RecoverPhysicalVolumesParams): Specifies the
            parameters to recover Physical Volumes.
        mount_volume_params (MountVolumeParams1): Specifies the parameters to
            mount Physical Volumes.
        recover_file_and_folder_params (RecoverFileAndFolderParams10):
            Specifies the parameters to perform a file and folder recovery.
        download_file_and_folder_params (DownloadFileAndFolderParams):
            Specifies the parameters to download files and folders.
        system_recovery_params (SystemRecoveryParams): Specifies the parameters to perform a system recovery.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "recovery_action":'recoveryAction',
        "recover_volume_params":'recoverVolumeParams',
        "mount_volume_params":'mountVolumeParams',
        "recover_file_and_folder_params":'recoverFileAndFolderParams',
        "download_file_and_folder_params":'downloadFileAndFolderParams',
        "system_recovery_params":'systemRecoveryParams'
    }

    def __init__(self,
                 objects=None,
                 recovery_action=None,
                 recover_volume_params=None,
                 mount_volume_params=None,
                 recover_file_and_folder_params=None,
                 download_file_and_folder_params=None,
                 system_recovery_params=None
                 ):
        """Constructor for the RecoverPhysicalEnvironmentParams class"""

        # Initialize members of the class
        self.objects = objects
        self.recovery_action = recovery_action
        self.recover_volume_params = recover_volume_params
        self.mount_volume_params = mount_volume_params
        self.recover_file_and_folder_params = recover_file_and_folder_params
        self.download_file_and_folder_params = download_file_and_folder_params
        self.system_recovery_params = system_recovery_params


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
        recover_volume_params = cohesity_management_sdk.models_v2.recover_physical_volumes_params.RecoverPhysicalVolumesParams.from_dictionary(dictionary.get('recoverVolumeParams')) if dictionary.get('recoverVolumeParams') else None
        mount_volume_params = cohesity_management_sdk.models_v2.mount_volume_params_1.MountVolumeParams1.from_dictionary(dictionary.get('mountVolumeParams')) if dictionary.get('mountVolumeParams') else None
        recover_file_and_folder_params = cohesity_management_sdk.models_v2.recover_file_and_folder_params_10.RecoverFileAndFolderParams10.from_dictionary(dictionary.get('recoverFileAndFolderParams')) if dictionary.get('recoverFileAndFolderParams') else None
        download_file_and_folder_params = cohesity_management_sdk.models_v2.download_file_and_folder_params.DownloadFileAndFolderParams.from_dictionary(dictionary.get('downloadFileAndFolderParams')) if dictionary.get('downloadFileAndFolderParams') else None
        system_recovery_params = cohesity_management_sdk.models_v2.system_recovery_params.SystemRecoveryParams.from_dictionary(
            dictionary.get('systemRecoveryParams')) if dictionary.get('systemRecoveryParams') else None

        # Return an object of this model
        return cls(objects,
                   recovery_action,
                   recover_volume_params,
                   mount_volume_params,
                   recover_file_and_folder_params,
                   download_file_and_folder_params,
                   system_recovery_params)