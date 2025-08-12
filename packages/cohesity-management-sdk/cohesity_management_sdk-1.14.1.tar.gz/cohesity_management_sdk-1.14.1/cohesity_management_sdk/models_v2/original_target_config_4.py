# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.target_vm_credentials_8

class OriginalTargetConfig4(object):

    """Implementation of the 'OriginalTargetConfig4' model.

    Specifies the configuration for recovering to the original target.

    Attributes:
        recover_method (RecoverMethodEnum): Specifies the method to recover
            files and folders.
        target_vm_credentials (TargetVmCredentials8): Specifies the
            credentials for the target VM. This is mandatory if the
            recoverMethod is AutoDeploy or UseHypervisorApis.
        recover_to_original_path (bool): Specifies whether to recover files
            and folders to the original path location. If false, alternatePath
            must be specified.
        alternate_path (string): Specifies the alternate path location to
            recover files to.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recover_method":'recoverMethod',
        "recover_to_original_path":'recoverToOriginalPath',
        "target_vm_credentials":'targetVmCredentials',
        "alternate_path":'alternatePath'
    }

    def __init__(self,
                 recover_method=None,
                 recover_to_original_path=None,
                 target_vm_credentials=None,
                 alternate_path=None):
        """Constructor for the OriginalTargetConfig4 class"""

        # Initialize members of the class
        self.recover_method = recover_method
        self.target_vm_credentials = target_vm_credentials
        self.recover_to_original_path = recover_to_original_path
        self.alternate_path = alternate_path


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
        recover_method = dictionary.get('recoverMethod')
        recover_to_original_path = dictionary.get('recoverToOriginalPath')
        target_vm_credentials = cohesity_management_sdk.models_v2.target_vm_credentials_8.TargetVmCredentials8.from_dictionary(dictionary.get('targetVmCredentials')) if dictionary.get('targetVmCredentials') else None
        alternate_path = dictionary.get('alternatePath')

        # Return an object of this model
        return cls(recover_method,
                   recover_to_original_path,
                   target_vm_credentials,
                   alternate_path)


