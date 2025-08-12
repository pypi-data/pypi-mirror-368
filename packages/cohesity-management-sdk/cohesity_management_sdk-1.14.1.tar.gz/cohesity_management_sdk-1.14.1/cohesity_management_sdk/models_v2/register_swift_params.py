# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.keystone_credentials

class RegisterSwiftParams(object):

    """Implementation of the 'RegisterSwiftParams' model.

    Specifies the parameters to register a Swift service on Keystone server.

    Attributes:
        tenant_id (string): Specifies the tenant Id who's Swift service will
            be registered.
        keystone_credentials (KeystoneCredentials): Specifies user credentials
            of a Keystone server.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "tenant_id":'tenantId',
        "keystone_credentials":'keystoneCredentials'
    }

    def __init__(self,
                 tenant_id=None,
                 keystone_credentials=None):
        """Constructor for the RegisterSwiftParams class"""

        # Initialize members of the class
        self.tenant_id = tenant_id
        self.keystone_credentials = keystone_credentials


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
        tenant_id = dictionary.get('tenantId')
        keystone_credentials = cohesity_management_sdk.models_v2.keystone_credentials.KeystoneCredentials.from_dictionary(dictionary.get('keystoneCredentials')) if dictionary.get('keystoneCredentials') else None

        # Return an object of this model
        return cls(tenant_id,
                   keystone_credentials)


