# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.user
import cohesity_management_sdk.models_v2.user_group
import cohesity_management_sdk.models_v2.tenant

class PermissionsInformation(object):

    """Implementation of the 'Permissions Information' model.

    Specifies the list of users, groups and users that have permissions for a
    given object.

    Attributes:
        object_id (long|int): Specifies the id of the object.
        users (list of User): Specifies the list of users which has the
            permissions to the object.
        groups (list of UserGroup): Specifies the list of user groups which
            has permissions to the object.
        tenant (Tenant): Specifies a tenant object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_id":'objectId',
        "users":'users',
        "groups":'groups',
        "tenant":'tenant'
    }

    def __init__(self,
                 object_id=None,
                 users=None,
                 groups=None,
                 tenant=None):
        """Constructor for the PermissionsInformation class"""

        # Initialize members of the class
        self.object_id = object_id
        self.users = users
        self.groups = groups
        self.tenant = tenant


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
        object_id = dictionary.get('objectId')
        users = None
        if dictionary.get("users") is not None:
            users = list()
            for structure in dictionary.get('users'):
                users.append(cohesity_management_sdk.models_v2.user.User.from_dictionary(structure))
        groups = None
        if dictionary.get("groups") is not None:
            groups = list()
            for structure in dictionary.get('groups'):
                groups.append(cohesity_management_sdk.models_v2.user_group.UserGroup.from_dictionary(structure))
        tenant = cohesity_management_sdk.models_v2.tenant.Tenant.from_dictionary(dictionary.get('tenant')) if dictionary.get('tenant') else None

        # Return an object of this model
        return cls(object_id,
                   users,
                   groups,
                   tenant)


