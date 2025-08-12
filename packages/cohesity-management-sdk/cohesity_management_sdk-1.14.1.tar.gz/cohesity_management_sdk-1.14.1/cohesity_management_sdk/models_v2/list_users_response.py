# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.user_params

class ListUsersResponse(object):

    """Implementation of the 'ListUsersResponse' model.

    Specifies a list of users

    Attributes:
        users (list of UserParams): Specifies the list of users.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "users":'users'
    }

    def __init__(self,
                 users=None):
        """Constructor for the ListUsersResponse class"""

        # Initialize members of the class
        self.users = users


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
        users = None
        if dictionary.get('users') is not None:
            users = list()
            for structure in dictionary.get('users'):
                users.append(cohesity_management_sdk.models_v2.user_params.UserParams.from_dictionary(structure))


        # Return an object of this model
        return cls(users)