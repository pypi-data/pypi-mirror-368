# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recovery_vlan_config

class RecoverToOriginalGPFSFilesTargetParams(object):

    """Implementation of the 'Recover To Original GPFS Files Target Params.' model.

    Specifies the params of the original GPFS recovery target.

    Attributes:
        recover_to_original_path (bool): Specifies whether to recover files
            and folders to the original path location. If false, alternatePath
            must be specified.
        alternate_path (string): Specifies the alternate path location to
            recover files to.
        overwrite_existing_file (bool): Specifies whether to overwrite
            existing file/folder during recovery.
        preserve_file_attributes (bool): Specifies whether to preserve
            file/folder attributes during recovery.
        continue_on_error (bool): Specifies whether to continue recovering
            other files if one of the files fails to recover. Default value is
            false.
        encryption_enabled (bool): Specifies whether encryption should be
            enabled during recovery.
        vlan_config (RecoveryVLANConfig): Specifies the VLAN configuration for
            Recovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recover_to_original_path":'recoverToOriginalPath',
        "alternate_path":'alternatePath',
        "overwrite_existing_file":'overwriteExistingFile',
        "preserve_file_attributes":'preserveFileAttributes',
        "continue_on_error":'continueOnError',
        "encryption_enabled":'encryptionEnabled',
        "vlan_config":'vlanConfig'
    }

    def __init__(self,
                 recover_to_original_path=None,
                 alternate_path=None,
                 overwrite_existing_file=None,
                 preserve_file_attributes=None,
                 continue_on_error=None,
                 encryption_enabled=None,
                 vlan_config=None):
        """Constructor for the RecoverToOriginalGPFSFilesTargetParams class"""

        # Initialize members of the class
        self.recover_to_original_path = recover_to_original_path
        self.alternate_path = alternate_path
        self.overwrite_existing_file = overwrite_existing_file
        self.preserve_file_attributes = preserve_file_attributes
        self.continue_on_error = continue_on_error
        self.encryption_enabled = encryption_enabled
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
        recover_to_original_path = dictionary.get('recoverToOriginalPath')
        alternate_path = dictionary.get('alternatePath')
        overwrite_existing_file = dictionary.get('overwriteExistingFile')
        preserve_file_attributes = dictionary.get('preserveFileAttributes')
        continue_on_error = dictionary.get('continueOnError')
        encryption_enabled = dictionary.get('encryptionEnabled')
        vlan_config = cohesity_management_sdk.models_v2.recovery_vlan_config.RecoveryVLANConfig.from_dictionary(dictionary.get('vlanConfig')) if dictionary.get('vlanConfig') else None

        # Return an object of this model
        return cls(recover_to_original_path,
                   alternate_path,
                   overwrite_existing_file,
                   preserve_file_attributes,
                   continue_on_error,
                   encryption_enabled,
                   vlan_config)


