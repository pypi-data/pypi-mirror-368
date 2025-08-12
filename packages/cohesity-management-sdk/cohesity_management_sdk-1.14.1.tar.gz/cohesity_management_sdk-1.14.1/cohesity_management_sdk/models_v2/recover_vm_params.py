# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_acropolis_snapshot_params
import cohesity_management_sdk.models_v2.recover_vm_params_6
import cohesity_management_sdk.models_v2.recover_acropolis_files_and_folders_params
import cohesity_management_sdk.models_v2.download_file_and_folder_params

class RecoverVMParams(object):

    """Implementation of the 'Recover VM params.' model.

    Specifies Acropolis related recovery options.

    Attributes:
        objects (list of RecoverAcropolisSnapshotParams): Specifies the
            list of recover Object parameters. This property is mandatory for
            all recovery action types except recover vms. While recovering
            VMs, a user can specify snapshots of VM's or a Protection Group
            Run details to recover all the VM's that are backed up by that
            Run. For recovering files, specifies the object contains the file
            to recover.
        recovery_action (RecoveryAction4Enum): Specifies the type of recovery
            action to be performed.
        recover_vm_params (RecoverVmParams6): Specifies the parameters to
            recover Acropolis VMs.
        recover_file_and_folder_params
            (RecoverAcropolisFilesAndFoldersParams): Specifies the parameters
            to recover Acropolis files and folders.
        download_file_and_folder_params (DownloadFileAndFolderParams):
            Specifies the parameters to download files and folders.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_action":'recoveryAction',
        "objects":'objects',
        "recover_vm_params":'recoverVmParams',
        "recover_file_and_folder_params":'recoverFileAndFolderParams',
        "download_file_and_folder_params":'downloadFileAndFolderParams'
    }

    def __init__(self,
                 recovery_action=None,
                 objects=None,
                 recover_vm_params=None,
                 recover_file_and_folder_params=None,
                 download_file_and_folder_params=None):
        """Constructor for the RecoverVMParams class"""

        # Initialize members of the class
        self.objects = objects
        self.recovery_action = recovery_action
        self.recover_vm_params = recover_vm_params
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
        recovery_action = dictionary.get('recoveryAction')
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.recover_acropolis_snapshot_params.RecoverAcropolisSnapshotParams.from_dictionary(structure))
        recover_vm_params = cohesity_management_sdk.models_v2.recover_vm_params_6.RecoverVmParams6.from_dictionary(dictionary.get('recoverVmParams')) if dictionary.get('recoverVmParams') else None
        recover_file_and_folder_params = cohesity_management_sdk.models_v2.recover_acropolis_files_and_folders_params.RecoverAcropolisFilesAndFoldersParams.from_dictionary(dictionary.get('recoverFileAndFolderParams')) if dictionary.get('recoverFileAndFolderParams') else None
        download_file_and_folder_params = cohesity_management_sdk.models_v2.download_file_and_folder_params.DownloadFileAndFolderParams.from_dictionary(dictionary.get('downloadFileAndFolderParams')) if dictionary.get('downloadFileAndFolderParams') else None

        # Return an object of this model
        return cls(recovery_action,
                   objects,
                   recover_vm_params,
                   recover_file_and_folder_params,
                   download_file_and_folder_params)