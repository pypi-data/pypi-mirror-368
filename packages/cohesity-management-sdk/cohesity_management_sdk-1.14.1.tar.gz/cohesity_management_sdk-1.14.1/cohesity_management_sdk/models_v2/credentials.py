# -*- coding: utf-8 -*-


class Credentials(object):

    """Implementation of the 'Credentials' model.

    Specifies the object to hold username and password.

    Attributes:
        username (string): Specifies the username to access target entity.
        password (string): Specifies the password to access target entity.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "username":'username',
        "password":'password'
    }

    def __init__(self,
                 username=None,
                 password=None):
        """Constructor for the Credentials class"""

        # Initialize members of the class
        self.username = username
        self.password = password


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
        username = dictionary.get('username')
        password = dictionary.get('password')

        # Return an object of this model
        return cls(username,
                   password)


