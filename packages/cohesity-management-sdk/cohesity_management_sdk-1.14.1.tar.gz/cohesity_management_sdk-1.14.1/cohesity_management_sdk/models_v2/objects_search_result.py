# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.search_object

class ObjectsSearchResult(object):

    """Implementation of the 'Objects Search Result' model.

    Specifies the Objects search result.

    Attributes:
        objects (list of SearchObject): Specifies the list of Objects.
        pagination_cookie (string): Specifies the pagination cookie with which
            subsequent parts of the response can be fetched.
        count (int): Specifies the number of objects to be fetched for the
            specified pagination cookie.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "pagination_cookie":'paginationCookie',
        "count":'count'
    }

    def __init__(self,
                 objects=None,
                 pagination_cookie=None,
                 count=None):
        """Constructor for the ObjectsSearchResult class"""

        # Initialize members of the class
        self.objects = objects
        self.pagination_cookie = pagination_cookie
        self.count = count


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
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.search_object.SearchObject.from_dictionary(structure))
        pagination_cookie = dictionary.get('paginationCookie')
        count = dictionary.get('count')

        # Return an object of this model
        return cls(objects,
                   pagination_cookie,
                   count)


