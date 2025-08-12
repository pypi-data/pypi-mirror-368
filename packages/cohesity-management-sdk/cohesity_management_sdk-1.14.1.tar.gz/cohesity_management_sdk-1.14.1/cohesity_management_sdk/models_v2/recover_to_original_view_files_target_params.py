# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models_v2.vlan_config

class RecoverToOriginalViewFilesTargetParams(object):

    """Implementation of the 'RecoverToOriginalViewFilesTargetParams' model.

    Specifies the params of the original View recovery target.

    Attributes:
        alternate_path (string): Specifies the alternate path location to recover files to.
        continue_on_error (bool): Specifies whether to continue recovering other files if one of the files fails to recover. Default value is false.
        overwrite_existing_file (bool): Specifies whether to overwrite existing file/folder during recovery.
        preserve_file_attributes (bool): Specifies whether to preserve file/folder attributes during recovery.
        recover_to_original_path (bool): Specifies whether to recover files and folders to the original path location. If false, alternatePath must be specified.
        vlan_config (VlanConfig): Specifies VLAN settings associated with the restore. If this is not specified, then the VLAN params will be automatically selected from one of the below options: a. If VLANs are configured on Cohesity, then the VLAN host/VIP will be automatically based on the client's (e.g. ESXI host) IP address. b. If VLANs are not configured on Cohesity, then the partition hostname or VIPs will be used for restores.
    """

    _names = {
        "alternate_path":"alternatePath",
        "continue_on_error":"continueOnError",
        "overwrite_existing_file":"overwriteExistingFile",
        "preserve_file_attributes":"preserveFileAttributes",
        "recover_to_original_path":"recoverToOriginalPath",
        "vlan_config":"vlanConfig",
    }

    def __init__(self,
                 alternate_path=None,
                 continue_on_error=None,
                 overwrite_existing_file=None,
                 preserve_file_attributes=None,
                 recover_to_original_path=None,
                 vlan_config=None):
        """Constructor for the RecoverToOriginalViewFilesTargetParams class"""

        self.alternate_path = alternate_path
        self.continue_on_error = continue_on_error
        self.overwrite_existing_file = overwrite_existing_file
        self.preserve_file_attributes = preserve_file_attributes
        self.recover_to_original_path = recover_to_original_path
        self.vlan_config = vlan_config


    @classmethod
    def from_dictionary(cls, dictionary):
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

        alternate_path = dictionary.get('alternatePath')
        continue_on_error = dictionary.get('continueOnError')
        overwrite_existing_file = dictionary.get('overwriteExistingFile')
        preserve_file_attributes = dictionary.get('preserveFileAttributes')
        recover_to_original_path = dictionary.get('recoverToOriginalPath')
        vlan_config = cohesity_management_sdk.models_v2.vlan_config.VlanConfig.from_dictionary(dictionary.get('vlanConfig')) if dictionary.get('vlanConfig') else None

        return cls(
            alternate_path,
            continue_on_error,
            overwrite_existing_file,
            preserve_file_attributes,
            recover_to_original_path,
            vlan_config
        )