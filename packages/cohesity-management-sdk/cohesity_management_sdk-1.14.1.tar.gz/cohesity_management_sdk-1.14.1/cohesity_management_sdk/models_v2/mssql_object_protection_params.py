# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.mssql_file_object_protection_params
import cohesity_management_sdk.models_v2.mssql_native_object_protection_params

class MssqlObjectProtectionParams(object):

    """Implementation of the 'MssqlObjectProtectionParams' model.

    Specifies the parameters specific to MSSQL Object Protection.

    Attributes:
        object_protection_type (ObjectProtectionTypeEnum): Specifies the MSSQL
            Object Protection type.
        file_object_protection_type_params (MssqlFileObjectProtectionParams):
            Specifies the params to create a File based MSSQL Object
            Protection.
        native_object_protection_type_params
            (MssqlNativeObjectProtectionParams): Specifies the params to
            create a Native based MSSQL Object Protection.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_protection_type":'objectProtectionType',
        "file_object_protection_type_params":'fileObjectProtectionTypeParams',
        "native_object_protection_type_params":'nativeObjectProtectionTypeParams'
    }

    def __init__(self,
                 object_protection_type=None,
                 file_object_protection_type_params=None,
                 native_object_protection_type_params=None):
        """Constructor for the MssqlObjectProtectionParams class"""

        # Initialize members of the class
        self.object_protection_type = object_protection_type
        self.file_object_protection_type_params = file_object_protection_type_params
        self.native_object_protection_type_params = native_object_protection_type_params


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
        file_object_protection_type_params = cohesity_management_sdk.models_v2.mssql_file_object_protection_params.MssqlFileObjectProtectionParams.from_dictionary(dictionary.get('fileObjectProtectionTypeParams')) if dictionary.get('fileObjectProtectionTypeParams') else None
        native_object_protection_type_params = cohesity_management_sdk.models_v2.mssql_native_object_protection_params.MssqlNativeObjectProtectionParams.from_dictionary(dictionary.get('nativeObjectProtectionTypeParams')) if dictionary.get('nativeObjectProtectionTypeParams') else None

        # Return an object of this model
        return cls(object_protection_type,
                   file_object_protection_type_params,
                   native_object_protection_type_params)


