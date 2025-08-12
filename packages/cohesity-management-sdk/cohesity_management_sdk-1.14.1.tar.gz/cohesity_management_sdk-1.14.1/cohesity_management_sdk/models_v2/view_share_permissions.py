# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.smb_permission

class ViewSharePermissions(object):

    """Implementation of the 'ViewSharePermissions' model.

    Specifies share permissions of the view.

    Attributes:
        super_user_sids (list of string): Specifies a list of super user
            sids.
        permissions (list of SMBPermission): Specifies a list of share
            permissions.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "super_user_sids":'superUserSids',
        "permissions":'permissions'
    }

    def __init__(self,
                 super_user_sids=None,
                 permissions=None):
        """Constructor for the ViewSharePermissions class"""

        # Initialize members of the class
        self.super_user_sids = super_user_sids
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
        super_user_sids = dictionary.get('superUserSids')
        permissions = None
        if dictionary.get("permissions") is not None:
            permissions = list()
            for structure in dictionary.get('permissions'):
                permissions.append(cohesity_management_sdk.models_v2.smb_permission.SMBPermission.from_dictionary(structure))

        # Return an object of this model
        return cls(super_user_sids,
                   permissions)


