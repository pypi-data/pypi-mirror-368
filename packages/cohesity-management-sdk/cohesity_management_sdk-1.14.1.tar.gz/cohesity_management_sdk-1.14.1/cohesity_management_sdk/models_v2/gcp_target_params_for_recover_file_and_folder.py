# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.target_vm
import cohesity_management_sdk.models_v2.target_vm_credentials_10
import cohesity_management_sdk.models_v2.vlan_config

class GCPTargetParamsForRecoverFileAndFolder(object):

    """Implementation of the 'GCP Target Params for Recover File And Folder' model.

    Specifies the parameters for a GCP recovery target.

    Attributes:
        target_vm (TargetVm): Specifies the target VM to recover files and
            folders to.
        recover_to_original_paths (bool): Specifies whether to recover files
            to original places.
        target_vm_credentials (TargetVmCredentials10): Specifies credentials
            to access the target VM.
        alternate_base_directory (string): Specifies a base directory under
            which all files and folders will be recovered. This is required if
            recoverToOriginalPaths is set to false.
        overwrite_originals (bool): Specifies whether to override the existing
            files. Default is true.
        preserve_attributes (bool): Specifies whether to preserve original
            attributes. Default is true.
        continue_on_error (bool): Specifies whether to continue recovering
            other files if one of files or folders failed to recover. Default
            value is false.
        vlan_config (VlanConfig): Specifies VLAN Params associated with the
            recovered files and folders. If this is not specified, then the
            VLAN settings will be automatically selected from one of the below
            options: a. If VLANs are configured on Cohesity, then the VLAN
            host/VIP will be automatically based on the client's (e.g. ESXI
            host) IP address. b. If VLANs are not configured on Cohesity, then
            the partition hostname or VIPs will be used for Recovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_vm":'targetVm',
        "recover_to_original_paths":'recoverToOriginalPaths',
        "target_vm_credentials":'targetVmCredentials',
        "alternate_base_directory":'alternateBaseDirectory',
        "overwrite_originals":'overwriteOriginals',
        "preserve_attributes":'preserveAttributes',
        "continue_on_error":'continueOnError',
        "vlan_config":'vlanConfig'
    }

    def __init__(self,
                 target_vm=None,
                 recover_to_original_paths=None,
                 target_vm_credentials=None,
                 alternate_base_directory=None,
                 overwrite_originals=None,
                 preserve_attributes=None,
                 continue_on_error=None,
                 vlan_config=None):
        """Constructor for the GCPTargetParamsForRecoverFileAndFolder class"""

        # Initialize members of the class
        self.target_vm = target_vm
        self.recover_to_original_paths = recover_to_original_paths
        self.target_vm_credentials = target_vm_credentials
        self.alternate_base_directory = alternate_base_directory
        self.overwrite_originals = overwrite_originals
        self.preserve_attributes = preserve_attributes
        self.continue_on_error = continue_on_error
        self.vlan_config = vlan_config


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
        target_vm = cohesity_management_sdk.models_v2.target_vm.TargetVm.from_dictionary(dictionary.get('targetVm')) if dictionary.get('targetVm') else None
        recover_to_original_paths = dictionary.get('recoverToOriginalPaths')
        target_vm_credentials = cohesity_management_sdk.models_v2.target_vm_credentials_10.TargetVmCredentials10.from_dictionary(dictionary.get('targetVmCredentials')) if dictionary.get('targetVmCredentials') else None
        alternate_base_directory = dictionary.get('alternateBaseDirectory')
        overwrite_originals = dictionary.get('overwriteOriginals')
        preserve_attributes = dictionary.get('preserveAttributes')
        continue_on_error = dictionary.get('continueOnError')
        vlan_config = cohesity_management_sdk.models_v2.vlan_config.VlanConfig.from_dictionary(dictionary.get('vlanConfig')) if dictionary.get('vlanConfig') else None

        # Return an object of this model
        return cls(target_vm,
                   recover_to_original_paths,
                   target_vm_credentials,
                   alternate_base_directory,
                   overwrite_originals,
                   preserve_attributes,
                   continue_on_error,
                   vlan_config)


