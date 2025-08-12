# -*- coding: utf-8 -*-


class CommonSearchIndexedObjectsResponseParams(object):

    """Implementation of the 'Common Search Indexed Objects Response Params.' model.

    Specifies the common search indexed objects response params.

    Attributes:
        object_type (ObjectType2Enum): Specifies the object type.
        count (int): Specifies the total number of indexed objects that match
            the filter and search criteria. Use this value to determine how
            many additional requests are required to get the full result.
        pagination_cookie (string): Specifies cookie for resuming search if
            pagination is being used.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_type":'objectType',
        "count":'count',
        "pagination_cookie":'paginationCookie'
    }

    def __init__(self,
                 object_type=None,
                 count=None,
                 pagination_cookie=None):
        """Constructor for the CommonSearchIndexedObjectsResponseParams class"""

        # Initialize members of the class
        self.object_type = object_type
        self.count = count
        self.pagination_cookie = pagination_cookie


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
        object_type = dictionary.get('objectType')
        count = dictionary.get('count')
        pagination_cookie = dictionary.get('paginationCookie')

        # Return an object of this model
        return cls(object_type,
                   count,
                   pagination_cookie)


