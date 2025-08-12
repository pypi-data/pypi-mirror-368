# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.admin_creds
import cohesity_management_sdk.models_v2.scope

class KeystoneCredentials(object):

    """Implementation of the 'KeystoneCredentials' model.

    Specifies user credentials of a Keystone server.

    Attributes:
        admin_creds (AdminCreds): Specifies parameters related to Keystone
            administrator.
        scope (Scope): Specifies parameters related to Keystone scope.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "admin_creds":'adminCreds',
        "scope":'scope'
    }

    def __init__(self,
                 admin_creds=None,
                 scope=None):
        """Constructor for the KeystoneCredentials class"""

        # Initialize members of the class
        self.admin_creds = admin_creds
        self.scope = scope


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
        admin_creds = cohesity_management_sdk.models_v2.admin_creds.AdminCreds.from_dictionary(dictionary.get('adminCreds')) if dictionary.get('adminCreds') else None
        scope = cohesity_management_sdk.models_v2.scope.Scope.from_dictionary(dictionary.get('scope')) if dictionary.get('scope') else None

        # Return an object of this model
        return cls(admin_creds,
                   scope)


