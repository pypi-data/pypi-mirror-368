# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_mssql_protection_group_request_params
import cohesity_management_sdk.models_v2.common_mssql_native_object_protection_params

class CommonMssqlObjectProtectionParams(object):

    """Implementation of the 'CommonMssqlObjectProtectionParams' model.

    Specifies the common parameters for MSSQL Object Protection.

    Attributes:
        object_protection_type (ObjectProtectionTypeEnum): Specifies the MSSQL
            Object Protection type.
        common_file_object_protection_type_params
            (CommonMSSQLProtectionGroupRequestParams): Specifies the common
            params to create a File based MSSQL Object Protection.
        common_native_object_protection_type_params
            (CommonMssqlNativeObjectProtectionParams): Specifies the common
            params to create a Native based MSSQL Object Protection.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_protection_type":'objectProtectionType',
        "common_file_object_protection_type_params":'commonFileObjectProtectionTypeParams',
        "common_native_object_protection_type_params":'commonNativeObjectProtectionTypeParams'
    }

    def __init__(self,
                 object_protection_type=None,
                 common_file_object_protection_type_params=None,
                 common_native_object_protection_type_params=None):
        """Constructor for the CommonMssqlObjectProtectionParams class"""

        # Initialize members of the class
        self.object_protection_type = object_protection_type
        self.common_file_object_protection_type_params = common_file_object_protection_type_params
        self.common_native_object_protection_type_params = common_native_object_protection_type_params


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
        object_protection_type = dictionary.get('objectProtectionType')
        common_file_object_protection_type_params = cohesity_management_sdk.models_v2.common_mssql_protection_group_request_params.CommonMSSQLProtectionGroupRequestParams.from_dictionary(dictionary.get('commonFileObjectProtectionTypeParams')) if dictionary.get('commonFileObjectProtectionTypeParams') else None
        common_native_object_protection_type_params = cohesity_management_sdk.models_v2.common_mssql_native_object_protection_params.CommonMssqlNativeObjectProtectionParams.from_dictionary(dictionary.get('commonNativeObjectProtectionTypeParams')) if dictionary.get('commonNativeObjectProtectionTypeParams') else None

        # Return an object of this model
        return cls(object_protection_type,
                   common_file_object_protection_type_params,
                   common_native_object_protection_type_params)


