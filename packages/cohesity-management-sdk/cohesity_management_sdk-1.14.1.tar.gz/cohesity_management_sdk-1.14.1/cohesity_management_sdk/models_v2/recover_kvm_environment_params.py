# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.recover_vm_params_4
import cohesity_management_sdk.models_v2.download_file_and_folder_params

class RecoverKVMEnvironmentParams(object):

    """Implementation of the 'Recover KVM environment params.' model.

    Specifies the recovery options specific to KVM environment.

    Attributes:
        objects (list of CommonRecoverObjectSnapshotParams): Specifies the
            list of recover Object parameters. This property is mandatory for
            all recovery action types except recover vms. While recovering
            VMs, a user can specify snapshots of VM's or a Protection Group
            Run details to recover all the VM's that are backed up by that
            Run.
        recovery_action (string): Specifies the type of recovery action to be
            performed.
        recover_vm_params (RecoverVmParams4): Specifies the parameters to
            recover KVM VM.
        download_file_and_folder_params (DownloadFileAndFolderParams):
            Specifies the parameters to download files and folders.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_action":'recoveryAction',
        "objects":'objects',
        "recover_vm_params":'recoverVmParams',
        "download_file_and_folder_params":'downloadFileAndFolderParams'
    }

    def __init__(self,
                 recovery_action='RecoverVMs',
                 objects=None,
                 recover_vm_params=None,
                 download_file_and_folder_params=None):
        """Constructor for the RecoverKVMEnvironmentParams class"""

        # Initialize members of the class
        self.objects = objects
        self.recovery_action = recovery_action
        self.recover_vm_params = recover_vm_params
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
        recovery_action = dictionary.get("recoveryAction") if dictionary.get("recoveryAction") else 'RecoverVMs'
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(structure))
        recover_vm_params = cohesity_management_sdk.models_v2.recover_vm_params_4.RecoverVmParams4.from_dictionary(dictionary.get('recoverVmParams')) if dictionary.get('recoverVmParams') else None
        download_file_and_folder_params = cohesity_management_sdk.models_v2.download_file_and_folder_params.DownloadFileAndFolderParams.from_dictionary(dictionary.get('downloadFileAndFolderParams')) if dictionary.get('downloadFileAndFolderParams') else None

        # Return an object of this model
        return cls(recovery_action,
                   objects,
                   recover_vm_params,
                   download_file_and_folder_params)


