# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_target
import cohesity_management_sdk.models_v2.target_vm_credentials

class NewTargetConfig(object):

    """Implementation of the 'NewTargetConfig' model.

    Specifies the configuration for recovering to a new target.

    Attributes:
        target_vm (RecoverTarget): Specifies the target VM to recover files
            and folders to.
        target_vm_credentials (TargetVmCredentials): Specifies the credentials
            for the target VM.
        absolute_path (string): Specifies the absolute path location to
            recover files to.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_vm":'targetVm',
        "target_vm_credentials":'targetVmCredentials',
        "absolute_path":'absolutePath'
    }

    def __init__(self,
                 target_vm=None,
                 target_vm_credentials=None,
                 absolute_path=None):
        """Constructor for the NewTargetConfig class"""

        # Initialize members of the class
        self.target_vm = target_vm
        self.target_vm_credentials = target_vm_credentials
        self.absolute_path = absolute_path


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
        target_vm = cohesity_management_sdk.models_v2.recover_target.RecoverTarget.from_dictionary(dictionary.get('targetVm')) if dictionary.get('targetVm') else None
        target_vm_credentials = cohesity_management_sdk.models_v2.target_vm_credentials.TargetVmCredentials.from_dictionary(dictionary.get('targetVmCredentials')) if dictionary.get('targetVmCredentials') else None
        absolute_path = dictionary.get('absolutePath')

        # Return an object of this model
        return cls(target_vm,
                   target_vm_credentials,
                   absolute_path)


