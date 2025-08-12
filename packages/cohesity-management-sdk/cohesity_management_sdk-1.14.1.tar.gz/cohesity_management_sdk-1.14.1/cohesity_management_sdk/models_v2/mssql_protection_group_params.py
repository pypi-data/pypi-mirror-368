# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.file_based_mssql_protection_group_request_params
import cohesity_management_sdk.models_v2.volume_based_mssql_protection_group_request_params
import cohesity_management_sdk.models_v2.native_based_mssql_protection_group_request_params

class MSSQLProtectionGroupParams(object):

    """Implementation of the 'MSSQL Protection Group Params.' model.

    Specifies the parameters specific to MSSQL Protection Group.

    Attributes:
        protection_type (ProtectionType6Enum): Specifies the MSSQL Protection
            Group type.
        file_protection_type_params
            (FileBasedMSSQLProtectionGroupRequestParams): Specifies the params
            to create a File based MSSQL Protection Group.
        volume_protection_type_params
            (VolumeBasedMSSQLProtectionGroupRequestParams): Specifies the
            params to create a Volume based MSSQL Protection Group.
        native_protection_type_params
            (NativeBasedMSSQLProtectionGroupRequestParams): Specifies the
            params to create a Native based MSSQL Protection Group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_type":'protectionType',
        "file_protection_type_params":'fileProtectionTypeParams',
        "volume_protection_type_params":'volumeProtectionTypeParams',
        "native_protection_type_params":'nativeProtectionTypeParams'
    }

    def __init__(self,
                 protection_type=None,
                 file_protection_type_params=None,
                 volume_protection_type_params=None,
                 native_protection_type_params=None):
        """Constructor for the MSSQLProtectionGroupParams class"""

        # Initialize members of the class
        self.protection_type = protection_type
        self.file_protection_type_params = file_protection_type_params
        self.volume_protection_type_params = volume_protection_type_params
        self.native_protection_type_params = native_protection_type_params


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
        protection_type = dictionary.get('protectionType')
        file_protection_type_params = cohesity_management_sdk.models_v2.file_based_mssql_protection_group_request_params.FileBasedMSSQLProtectionGroupRequestParams.from_dictionary(dictionary.get('fileProtectionTypeParams')) if dictionary.get('fileProtectionTypeParams') else None
        volume_protection_type_params = cohesity_management_sdk.models_v2.volume_based_mssql_protection_group_request_params.VolumeBasedMSSQLProtectionGroupRequestParams.from_dictionary(dictionary.get('volumeProtectionTypeParams')) if dictionary.get('volumeProtectionTypeParams') else None
        native_protection_type_params = cohesity_management_sdk.models_v2.native_based_mssql_protection_group_request_params.NativeBasedMSSQLProtectionGroupRequestParams.from_dictionary(dictionary.get('nativeProtectionTypeParams')) if dictionary.get('nativeProtectionTypeParams') else None

        # Return an object of this model
        return cls(protection_type,
                   file_protection_type_params,
                   volume_protection_type_params,
                   native_protection_type_params)


