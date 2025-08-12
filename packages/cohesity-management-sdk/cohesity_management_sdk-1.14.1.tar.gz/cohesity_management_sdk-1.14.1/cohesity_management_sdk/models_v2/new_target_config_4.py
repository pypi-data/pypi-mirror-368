# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_target
import cohesity_management_sdk.models_v2.target_vm_credentials_8

class NewTargetConfig4(object):

    """Implementation of the 'NewTargetConfig4' model.

    Specifies the configuration for recovering to a new target.

    Attributes:
        target_vm (RecoverTarget): Specifies the target VM to recover files
            and folders to.
        recover_method (RecoverMethodEnum): Specifies the method to recover
            files and folders.
        target_vm_credentials (TargetVmCredentials8): Specifies the
            credentials for the target VM. This is mandatory if the
            recoverMethod is AutoDeploy or UseHypervisorApis.
        absolute_path (string): Specifies the path location to recover files
            to.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_vm":'targetVm',
        "recover_method":'recoverMethod',
        "absolute_path":'absolutePath',
        "target_vm_credentials":'targetVmCredentials'
    }

    def __init__(self,
                 target_vm=None,
                 recover_method=None,
                 absolute_path=None,
                 target_vm_credentials=None):
        """Constructor for the NewTargetConfig4 class"""

        # Initialize members of the class
        self.target_vm = target_vm
        self.recover_method = recover_method
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
        recover_method = dictionary.get('recoverMethod')
        absolute_path = dictionary.get('absolutePath')
        target_vm_credentials = cohesity_management_sdk.models_v2.target_vm_credentials_8.TargetVmCredentials8.from_dictionary(dictionary.get('targetVmCredentials')) if dictionary.get('targetVmCredentials') else None

        # Return an object of this model
        return cls(target_vm,
                   recover_method,
                   absolute_path,
                   target_vm_credentials)


