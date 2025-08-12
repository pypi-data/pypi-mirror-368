# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.recover_gcpvm_params
import cohesity_management_sdk.models_v2.download_file_and_folder_params
import cohesity_management_sdk.models_v2.recover_gcp_file_and_folder_params

class RecoverGCPEnvironmentParams(object):

    """Implementation of the 'Recover GCP environment params.' model.

    Specifies the recovery options specific to GCP environment.

    Attributes:
        download_file_and_folder_params (DownloadFileAndFolderParams): Specifies the parameters to download files and folders
        objects (list of CommonRecoverObjectSnapshotParams): Specifies the
            list of recover Object parameters. This property is mandatory for
            all recovery action types except recover vms. While recovering
            VMs, a user can specify snapshots of VM's or a Protection Group
            Run details to recover all the VM's that are backed up by that
            Run.
        recovery_action (string): Specifies the type of recover action to be
            performed.
        recover_file_and_folder_params (RecoverGCPFileAndFolderParams): Specifies the parameters to recover files and folders.
        recover_vm_params (RecoverGCPVMParams): Specifies the parameters to
            recover GCP VM.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "download_file_and_folder_params":'downloadFileAndFolderParams',
        "recovery_action":'recoveryAction',
        "objects":'objects',
        "recover_file_and_folder_params":'recoverFileAndFolderParams',
        "recover_vm_params":'recoverVmParams'
    }

    def __init__(self,
                 download_file_and_folder_params=None,
                 recovery_action='RecoverVMs',
                 objects=None,
                 recover_file_and_folder_params=None,
                 recover_vm_params=None):
        """Constructor for the RecoverGCPEnvironmentParams class"""

        # Initialize members of the class
        self.download_file_and_folder_params = download_file_and_folder_params
        self.objects = objects
        self.recovery_action = recovery_action
        self.recover_file_and_folder_params = recover_file_and_folder_params
        self.recover_vm_params = recover_vm_params


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
        download_file_and_folder_params = cohesity_management_sdk.models_v2.download_file_and_folder_params.DownloadFileAndFolderParams.from_dictionary(
            dictionary.get('downloadFileAndFolderParams')) if dictionary.get('downloadFileAndFolderParams') else None
        recovery_action = dictionary.get("recoveryAction") if dictionary.get("recoveryAction") else 'RecoverVMs'
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(structure))
        recover_file_and_folder_params = cohesity_management_sdk.models_v2.recover_gcp_file_and_folder_params.RecoverGCPFileAndFolderParams.from_dictionary(dictionary.get('recoverFileAndFolderParams')) if dictionary.get('recoverFileAndFolderParams') else None
        recover_vm_params = cohesity_management_sdk.models_v2.recover_gcpvm_params.RecoverGCPVMParams.from_dictionary(dictionary.get('recoverVmParams')) if dictionary.get('recoverVmParams') else None

        # Return an object of this model
        return cls(download_file_and_folder_params,
                   recovery_action,
                   objects,
                   recover_file_and_folder_params,
                   recover_vm_params)