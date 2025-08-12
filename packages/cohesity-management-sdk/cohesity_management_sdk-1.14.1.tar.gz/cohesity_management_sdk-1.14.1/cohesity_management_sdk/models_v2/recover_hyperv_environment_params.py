# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.recover_vm_params_7
import cohesity_management_sdk.models_v2.mount_volume_params_2
import cohesity_management_sdk.models_v2.recover_hyperv_file_and_folder_params
import cohesity_management_sdk.models_v2.download_file_and_folder_params

class RecoverHypervEnvironmentParams(object):

    """Implementation of the 'Recover HyperV environment params.' model.

    Specifies the recovery options specific to HyperV environment.

    Attributes:
        objects (list of CommonRecoverObjectSnapshotParams): Specifies the
            list of recover Object parameters. This property is mandatory for
            all recovery action types except recover vms. While recovering
            VMs, a user can specify snapshots of VM's or a Protection Group
            Run details to recover all the VM's that are backed up by that
            Run. For recovering files, specifies the object contains the file
            to recover.
        recovery_action (RecoveryAction12Enum): Specifies the type of recovery
            action to be performed.
        recover_vm_params (RecoverVmParams7): Specifies the parameters to
            recover HyperV VM.
        mount_volume_params (MountVolumeParams2): Specifies the parameters to
            mount HyperV Volumes.
        recover_file_and_folder_params (RecoverHypervFileAndFolderParams):
            Specifies the parameters to recover files and folders.
        download_file_and_folder_params (DownloadFileAndFolderParams):
            Specifies the parameters to download files and folders.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_action":'recoveryAction',
        "objects":'objects',
        "recover_vm_params":'recoverVmParams',
        "mount_volume_params":'mountVolumeParams',
        "recover_file_and_folder_params":'recoverFileAndFolderParams',
        "download_file_and_folder_params":'downloadFileAndFolderParams'
    }

    def __init__(self,
                 recovery_action=None,
                 objects=None,
                 recover_vm_params=None,
                 mount_volume_params=None,
                 recover_file_and_folder_params=None,
                 download_file_and_folder_params=None):
        """Constructor for the RecoverHypervEnvironmentParams class"""

        # Initialize members of the class
        self.objects = objects
        self.recovery_action = recovery_action
        self.recover_vm_params = recover_vm_params
        self.mount_volume_params = mount_volume_params
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
                objects.append(cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(structure))
        recover_vm_params = cohesity_management_sdk.models_v2.recover_vm_params_7.RecoverVmParams7.from_dictionary(dictionary.get('recoverVmParams')) if dictionary.get('recoverVmParams') else None
        mount_volume_params = cohesity_management_sdk.models_v2.mount_volume_params_2.MountVolumeParams2.from_dictionary(dictionary.get('mountVolumeParams')) if dictionary.get('mountVolumeParams') else None
        recover_file_and_folder_params = cohesity_management_sdk.models_v2.recover_hyperv_file_and_folder_params.RecoverHypervFileAndFolderParams.from_dictionary(dictionary.get('recoverFileAndFolderParams')) if dictionary.get('recoverFileAndFolderParams') else None
        download_file_and_folder_params = cohesity_management_sdk.models_v2.download_file_and_folder_params.DownloadFileAndFolderParams.from_dictionary(dictionary.get('downloadFileAndFolderParams')) if dictionary.get('downloadFileAndFolderParams') else None

        # Return an object of this model
        return cls(recovery_action,
                   objects,
                   recover_vm_params,
                   mount_volume_params,
                   recover_file_and_folder_params,
                   download_file_and_folder_params)


