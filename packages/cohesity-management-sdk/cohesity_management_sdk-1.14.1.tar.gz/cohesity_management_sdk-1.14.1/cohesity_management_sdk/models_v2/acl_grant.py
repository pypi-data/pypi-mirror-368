# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.grantee

class AclGrant(object):

    """Implementation of the 'AclGrant' model.

    Specifies an ACL grant.

    Attributes:
        grantee (Grantee): Specifies the grantee.
        permissions (list of PermissionEnum): Specifies a list of permissions
            granted to the grantees.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "grantee":'grantee',
        "permissions":'permissions'
    }

    def __init__(self,
                 grantee=None,
                 permissions=None):
        """Constructor for the AclGrant class"""

        # Initialize members of the class
        self.grantee = grantee
        self.permissions = permissions


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
        grantee = cohesity_management_sdk.models_v2.grantee.Grantee.from_dictionary(dictionary.get('grantee')) if dictionary.get('grantee') else None
        permissions = dictionary.get('permissions')

        # Return an object of this model
        return cls(grantee,
                   permissions)


