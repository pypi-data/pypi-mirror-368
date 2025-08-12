# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.target_vm_credentials

class AcropolisRecoverFilesOriginalTargetConfig(object):

    """Implementation of the 'Acropolis Recover Files Original Target Config.' model.

    Specifies the configuration for recovering files and folders to the
    original target.

    Attributes:
        target_vm_credentials (TargetVmCredentials): Specifies the credentials
            for the target VM.
        recover_to_original_path (bool): Specifies whether to recover files
            and folders to the original path location. If false, alternatePath
            must be specified.
        alternate_path (string): Specifies the alternate path location to
            recover files to.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_vm_credentials":'targetVmCredentials',
        "recover_to_original_path":'recoverToOriginalPath',
        "alternate_path":'alternatePath'
    }

    def __init__(self,
                 target_vm_credentials=None,
                 recover_to_original_path=None,
                 alternate_path=None):
        """Constructor for the AcropolisRecoverFilesOriginalTargetConfig class"""

        # Initialize members of the class
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
        target_vm_credentials = cohesity_management_sdk.models_v2.target_vm_credentials.TargetVmCredentials.from_dictionary(dictionary.get('targetVmCredentials')) if dictionary.get('targetVmCredentials') else None
        recover_to_original_path = dictionary.get('recoverToOriginalPath')
        alternate_path = dictionary.get('alternatePath')

        # Return an object of this model
        return cls(target_vm_credentials,
                   recover_to_original_path,
                   alternate_path)


