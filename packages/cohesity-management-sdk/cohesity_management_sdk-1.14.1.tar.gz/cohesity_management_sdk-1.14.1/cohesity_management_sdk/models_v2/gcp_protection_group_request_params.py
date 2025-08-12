# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.gcp_native_protection_group_request_params

class GCPProtectionGroupRequestParams(object):

    """Implementation of the 'GCP Protection Group Request Params.' model.

    Specifies the parameters which are specific to GCP related Protection
    Groups.

    Attributes:
        protection_type (string): Specifies the GCP Protection Group type.
        native_protection_type_params (GCPNativeProtectionGroupRequestParams):
            Specifies the parameters which are specific to GCP related
            Protection Groups using GCP native snapshot APIs. Atlease one of
            tags or objects must be specified.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_type":'protectionType',
        "native_protection_type_params":'nativeProtectionTypeParams'
    }

    def __init__(self,
                 protection_type='kNative',
                 native_protection_type_params=None):
        """Constructor for the GCPProtectionGroupRequestParams class"""

        # Initialize members of the class
        self.protection_type = protection_type
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
        protection_type = dictionary.get("protectionType") if dictionary.get("protectionType") else 'kNative'
        native_protection_type_params = cohesity_management_sdk.models_v2.gcp_native_protection_group_request_params.GCPNativeProtectionGroupRequestParams.from_dictionary(dictionary.get('nativeProtectionTypeParams')) if dictionary.get('nativeProtectionTypeParams') else None

        # Return an object of this model
        return cls(protection_type,
                   native_protection_type_params)


