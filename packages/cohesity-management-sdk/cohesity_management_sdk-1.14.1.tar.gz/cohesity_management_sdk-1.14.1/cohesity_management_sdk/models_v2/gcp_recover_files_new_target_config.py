# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_target
import cohesity_management_sdk.models_v2.credentials

class GCPRecoverFilesNewTargetConfig(object):

    """Implementation of the 'GCPRecoverFilesNewTargetConfig'' model.

    Specifies the configuration for recovering files and folders to a
      new target.

    Attributes:
        absolute_path (string): Specifies the path location to recover files to.
        target_vm (RecoverTarget): Specifies the target VM to recover files and folders to.
        target_vm_credentials (Credentials): Specifies the credentials for the target VM.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "absolute_path":'absolutePath',
        "target_vm":'targetVm',
        "target_vm_credentials":'targetVmCredentials'
    }

    def __init__(self,
                 absolute_path=None,
                 target_vm=None,
                 target_vm_credentials=None):
        """Constructor for the GCPRecoverFilesNewTargetConfig class"""

        # Initialize members of the class
        self.absolute_path = absolute_path
        self.target_vm = target_vm
        self.target_vm_credentials = target_vm_credentials


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
        absolute_path = dictionary.get('absolutePath')
        target_vm = cohesity_management_sdk.models_v2.recover_target.RecoverTarget.from_dictionary(dictionary.get('targetVm')) if dictionary.get('targetVm') else None
        target_vm_credentials = cohesity_management_sdk.models_v2.credentials.Credentials.from_dictionary(dictionary.get('targetVmCredentials')) if dictionary.get('targetVmCredentials') else None

        # Return an object of this model
        return cls(absolute_path,
                   target_vm,
                   target_vm_credentials)