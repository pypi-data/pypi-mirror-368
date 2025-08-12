# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_file_and_folder_info
import cohesity_management_sdk.models_v2.vmware_target_params_5

class RecoverVmwareFileAndFolderParams(object):

    """Implementation of the Recover VMware File And Folder Params model.

    Specifies the parameters to recover files and folders.

    Attributes:
        glacier_retrieval_type (GlacierRetrievalTypeEnum): Specifies the glacier retrieval type when restoring or downloding
          files or folders from a Glacier-based cloud snapshot.
        parent_recovery_id (string): If current recovery is child task triggered through another parent
          recovery operation, then this field will specify the id of the parent recovery.
        pattern: "^\d+:\d+:\d+$"
        files_and_folders (list of CommonFileAndFolderInfo): Specifies the
            info about the files and folders to be recovered.
        target_environment (string): Specifies the environment of the recovery
            target. The corresponding params below must be filled out.
        vmware_target_params (VmwareTargetParams5): Specifies the parameters
            to recover to a VMware target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "glacier_retrieval_type":'glacierRetrievalType',
        "parent_recovery_id":'parentRecoveryId',
        "files_and_folders":'filesAndFolders',
        "target_environment":'targetEnvironment',
        "vmware_target_params":'vmwareTargetParams'
    }

    def __init__(self,
                 glacier_retrieval_type=None,
                 parent_recovery_id=None,
                 files_and_folders=None,
                 target_environment='kVMware',
                 vmware_target_params=None):
        """Constructor for the RecoverVmwareFileAndFolderParams class"""

        # Initialize members of the class
        self.glacier_retrieval_type = glacier_retrieval_type
        self.parent_recovery_id = parent_recovery_id
        self.files_and_folders = files_and_folders
        self.target_environment = target_environment
        self.vmware_target_params = vmware_target_params


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
        glacier_retrieval_type = dictionary.get('glacierRetrievalType')
        parent_recovery_id = dictionary.get('parentRecoveryId')
        files_and_folders = None
        if dictionary.get("filesAndFolders") is not None:
            files_and_folders = list()
            for structure in dictionary.get('filesAndFolders'):
                files_and_folders.append(cohesity_management_sdk.models_v2.common_file_and_folder_info.CommonFileAndFolderInfo.from_dictionary(structure))
        target_environment = dictionary.get("targetEnvironment") if dictionary.get("targetEnvironment") else 'kVMware'
        vmware_target_params = cohesity_management_sdk.models_v2.vmware_target_params_5.VmwareTargetParams5.from_dictionary(dictionary.get('vmwareTargetParams')) if dictionary.get('vmwareTargetParams') else None

        # Return an object of this model
        return cls(glacier_retrieval_type,
                   parent_recovery_id,
                   files_and_folders,
                   target_environment,
                   vmware_target_params)