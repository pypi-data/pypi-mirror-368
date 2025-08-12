# -*- coding: utf-8 -*-


class PaginationInfo(object):

    """Implementation of the 'PaginationInfo' model.

    Specifies information needed to support pagination.

    Attributes:
        cookie (string): Specifies a cookie which can be passed in by the user
            in order to retrieve the next page of results.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cookie":'cookie'
    }

    def __init__(self,
                 cookie=None):
        """Constructor for the PaginationInfo class"""

        # Initialize members of the class
        self.cookie = cookie


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
        cookie = dictionary.get('cookie')

        # Return an object of this model
        return cls(cookie)


