# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protection_group

class ProtectionGroups(object):

    """Implementation of the 'ProtectionGroups' model.

    Protection Group  response.

    Attributes:
        pagination_cookie (string): Specifies the information needed in order to support pagination.
          This will not be included for the last page of results.
        protection_groups (list of ProtectionGroup): Specifies the list of
            Protection Groups which were returned by the request.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "pagination_cookie":'paginationCookie',
        "protection_groups":'protectionGroups'
    }

    def __init__(self,
                 pagination_cookie=None,
                 protection_groups=None):
        """Constructor for the ProtectionGroups class"""

        # Initialize members of the class
        self.pagination_cookie = pagination_cookie
        self.protection_groups = protection_groups


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
        pagination_cookie = dictionary.get('paginationCookie')
        protection_groups = None
        if dictionary.get("protectionGroups") is not None:
            protection_groups = list()
            for structure in dictionary.get('protectionGroups'):
                protection_groups.append(cohesity_management_sdk.models_v2.protection_group.ProtectionGroup.from_dictionary(structure))

        # Return an object of this model
        return cls(pagination_cookie,
                   protection_groups)