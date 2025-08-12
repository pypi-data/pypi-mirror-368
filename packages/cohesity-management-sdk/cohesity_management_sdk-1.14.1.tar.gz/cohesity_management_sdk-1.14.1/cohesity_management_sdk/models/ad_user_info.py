# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class ADUserInfo(object):

    """Implementation of the 'ADUserInfo' model.

    Specifies an AD User''s information logged in using an active directory.
    This information is not stored on the Cluster.

    Attributes:
        group_sids (list of  string): Specifies the SIDs of the groups.
        groups (list of string): Specifies the groups this user is a part of.
        is_floating_user (bool): Specifies whether this is a floating user or not.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "group_sids":'groupSids',
        "groups":'groups',
        "is_floating_user":'isFloatingUser'
    }

    def __init__(self,
                 group_sids=None,
                 groups=None,
                 is_floating_user=None):
        """Constructor for the ADUserInfo class"""

        # Initialize members of the class
        self.group_sids = group_sids
        self.groups = groups
        self.is_floating_user = is_floating_user


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
        group_sids = dictionary.get('groupSids')
        groups = dictionary.get('groups')
        is_floating_user = dictionary.get('isFloatingUser')

        # Return an object of this model
        return cls(group_sids,
                   groups,
                   is_floating_user)


