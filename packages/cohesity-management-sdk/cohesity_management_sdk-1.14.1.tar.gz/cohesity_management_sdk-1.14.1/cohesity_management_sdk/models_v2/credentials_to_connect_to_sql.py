# -*- coding: utf-8 -*-


class CredentialsToConnectToSQL(object):

    """Implementation of the 'Credentials to connect to SQL.' model.

    Specifies the credentials to connect to SQL.

    Attributes:
        username (string): username for when agent is not installed
        password (string): password for when agent is not installed

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "username":'username',
        "password":'password'
    }

    def __init__(self,
                 username=None,
                 password=None):
        """Constructor for the CredentialsToConnectToSQL class"""

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


