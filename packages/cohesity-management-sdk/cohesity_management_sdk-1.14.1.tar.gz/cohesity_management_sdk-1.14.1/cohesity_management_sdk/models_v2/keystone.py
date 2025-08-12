# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.admin_creds
import cohesity_management_sdk.models_v2.scope

class Keystone(object):

    """Implementation of the 'Keystone' model.

    Specifies a Keystone.

    Attributes:
        name (string): Specifies the Keystone configuration name.
        id (long|int): Specifies the Keystone configuration id.
        auth_url (string): Specifies the url points to the Keystone service.
        admin_creds (AdminCreds): Specifies parameters related to Keystone
            administrator.
        scope (Scope): Specifies parameters related to Keystone scope.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "auth_url":'authUrl',
        "admin_creds":'adminCreds',
        "id":'id',
        "scope":'scope'
    }

    def __init__(self,
                 name=None,
                 auth_url=None,
                 admin_creds=None,
                 id=None,
                 scope=None):
        """Constructor for the Keystone class"""

        # Initialize members of the class
        self.name = name
        self.id = id
        self.auth_url = auth_url
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
        name = dictionary.get('name')
        auth_url = dictionary.get('authUrl')
        admin_creds = cohesity_management_sdk.models_v2.admin_creds.AdminCreds.from_dictionary(dictionary.get('adminCreds')) if dictionary.get('adminCreds') else None
        id = dictionary.get('id')
        scope = cohesity_management_sdk.models_v2.scope.Scope.from_dictionary(dictionary.get('scope')) if dictionary.get('scope') else None

        # Return an object of this model
        return cls(name,
                   auth_url,
                   admin_creds,
                   id,
                   scope)


