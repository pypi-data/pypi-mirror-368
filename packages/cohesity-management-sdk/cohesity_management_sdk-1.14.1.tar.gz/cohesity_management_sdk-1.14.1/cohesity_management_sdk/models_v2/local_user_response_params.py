# -*- coding: utf-8 -*-

class LocalUserResponseParams(object):

    """Implementation of the 'LocalUserResponseParams' model.

    Specifies properties for LOCAL cohesity user.

    Attributes:
        email (string): Specifies the email address of the User.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "email":'email'
    }

    def __init__(self, email=None):
        """Constructor for the LocalUserResponseParams class"""

        # Initialize members of the class
        self.email = email


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
        email = dictionary.get('email')

        # Return an object of this model
        return cls(email)