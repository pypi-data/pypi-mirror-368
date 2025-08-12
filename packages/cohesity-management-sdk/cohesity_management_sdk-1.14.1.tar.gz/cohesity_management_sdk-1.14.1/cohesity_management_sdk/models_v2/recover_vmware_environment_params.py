# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_vmware_parent_snapshot_params
import cohesity_management_sdk.models_v2.recover_vmware_vm_params_1
import cohesity_management_sdk.models_v2.recover_vm_disk_params
import cohesity_management_sdk.models_v2.mount_vmware_volumes_params
import cohesity_management_sdk.models_v2.recover_v_app_params
import cohesity_management_sdk.models_v2.recover_v_app_template_params
import cohesity_management_sdk.models_v2.recover_vmware_file_and_folder_params
import cohesity_management_sdk.models_v2.download_file_and_folder_params

class RecoverVmwareEnvironmentParams(object):

    """Implementation of the 'Recover VMware environment params.' model.

    Specifies the recovery options specific to VMware environment.

    Attributes:
        objects (list of RecoverVmwareParentSnapshotParams): Specifies the list of
            recover Object parameters. This property is mandatory for all
            recovery action types except recover vms. While recovering VMs, a
            user can specify snapshots of VM's or a Protection Group Run
            details to recover all the VM's that are backed up by that Run.
            For recovering files, specifies the object contains the file to
            recover.
        recovery_action (RecoveryAction1Enum): Specifies the type of recovery
            action to be performed.
        recover_vm_params (RecoverVmwareVMParams1): Specifies the parameters
            to recover VMware VM.
        recover_vm_disk_params (RecoverVmDiskParams): Specifies the parameters
            to recover VMware Disks.
        mount_volume_params (MountVmwareVolumesParams): Specifies the
            parameters to mount VMware Volumes.
        recover_v_app_params (RecoverVAppParams): Specifies the parameters to
            recover a VMware vApp.
        recover_v_app_template_params (RecoverVAppTemplateParams): Specifies
            the parameters to recover a VMware vApp template.
        recover_file_and_folder_params (RecoverVmwareFileAndFolderParams):
            Specifies the parameters to recover files and folders.
        download_file_and_folder_params (DownloadFileAndFolderParams):
            Specifies the parameters to download files and folders.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_action":'recoveryAction',
        "objects":'objects',
        "recover_vm_params":'recoverVmParams',
        "recover_vm_disk_params":'recoverVmDiskParams',
        "mount_volume_params":'mountVolumeParams',
        "recover_v_app_params":'recoverVAppParams',
        "recover_v_app_template_params":'recoverVAppTemplateParams',
        "recover_file_and_folder_params":'recoverFileAndFolderParams',
        "download_file_and_folder_params":'downloadFileAndFolderParams'
    }

    def __init__(self,
                 recovery_action=None,
                 objects=None,
                 recover_vm_params=None,
                 recover_vm_disk_params=None,
                 mount_volume_params=None,
                 recover_v_app_params=None,
                 recover_v_app_template_params=None,
                 recover_file_and_folder_params=None,
                 download_file_and_folder_params=None):
        """Constructor for the RecoverVmwareEnvironmentParams class"""

        # Initialize members of the class
        self.objects = objects
        self.recovery_action = recovery_action
        self.recover_vm_params = recover_vm_params
        self.recover_vm_disk_params = recover_vm_disk_params
        self.mount_volume_params = mount_volume_params
        self.recover_v_app_params = recover_v_app_params
        self.recover_v_app_template_params = recover_v_app_template_params
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
                objects.append(cohesity_management_sdk.models_v2.recover_vmware_parent_snapshot_params.RecoverVmwareParentSnapshotParams.from_dictionary(structure))
        recover_vm_params = cohesity_management_sdk.models_v2.recover_vmware_vm_params_1.RecoverVmwareVMParams1.from_dictionary(dictionary.get('recoverVmParams')) if dictionary.get('recoverVmParams') else None
        recover_vm_disk_params = cohesity_management_sdk.models_v2.recover_vm_disk_params.RecoverVmDiskParams.from_dictionary(dictionary.get('recoverVmDiskParams')) if dictionary.get('recoverVmDiskParams') else None
        mount_volume_params = cohesity_management_sdk.models_v2.mount_vmware_volumes_params.MountVmwareVolumesParams.from_dictionary(dictionary.get('mountVolumeParams')) if dictionary.get('mountVolumeParams') else None
        recover_v_app_params = cohesity_management_sdk.models_v2.recover_v_app_params.RecoverVAppParams.from_dictionary(dictionary.get('recoverVAppParams')) if dictionary.get('recoverVAppParams') else None
        recover_v_app_template_params = cohesity_management_sdk.models_v2.recover_v_app_template_params.RecoverVAppTemplateParams.from_dictionary(dictionary.get('recoverVAppTemplateParams')) if dictionary.get('recoverVAppTemplateParams') else None
        recover_file_and_folder_params = cohesity_management_sdk.models_v2.recover_vmware_file_and_folder_params.RecoverVmwareFileAndFolderParams.from_dictionary(dictionary.get('recoverFileAndFolderParams')) if dictionary.get('recoverFileAndFolderParams') else None
        download_file_and_folder_params = cohesity_management_sdk.models_v2.download_file_and_folder_params.DownloadFileAndFolderParams.from_dictionary(dictionary.get('downloadFileAndFolderParams')) if dictionary.get('downloadFileAndFolderParams') else None

        # Return an object of this model
        return cls(recovery_action,
                   objects,
                   recover_vm_params,
                   recover_vm_disk_params,
                   mount_volume_params,
                   recover_v_app_params,
                   recover_v_app_template_params,
                   recover_file_and_folder_params,
                   download_file_and_folder_params)