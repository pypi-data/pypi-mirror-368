# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.credentials

class GCPRecoverFilesOriginalTargetConfig(object):

    """Implementation of the 'GCPRecoverFilesOriginalTargetConfig'' model.

    Specifies the configuration for recovering files and folders to the
      original target.

    Attributes:
        alternate_path (string): Specifies the alternate path location to recover files to.
        recover_to_original_path (bool): Specifies whether to recover files and folders to the original
          path location. If false, alternatePath must be specified.
        target_vm_credentials (Credentials): Specifies the credentials for the target VM.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "alternate_path":'alternatePath',
        "recover_to_original_path":'recoverToOriginalPath',
        "target_vm_credentials":'targetVmCredentials'
    }

    def __init__(self,
                 alternate_path=None,
                 recover_to_original_path=None,
                 target_vm_credentials=None):
        """Constructor for the GCPRecoverFilesOriginalTargetConfig class"""

        # Initialize members of the class
        self.alternate_path = alternate_path
        self.recover_to_original_path = recover_to_original_path
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
        alternate_path = dictionary.get('alternatePath')
        recover_to_original_path = dictionary.get('recoverToOriginalPath')
        target_vm_credentials = cohesity_management_sdk.models_v2.credentials.Credentials.from_dictionary(dictionary.get('targetVmCredentials')) if dictionary.get('targetVmCredentials') else None

        # Return an object of this model
        return cls(alternate_path,
                   recover_to_original_path,
                   target_vm_credentials)