# -*- coding: utf-8 -*-


class SMBMountCredentials(object):

    """Implementation of the 'SMB Mount Credentials.' model.

    Specifies the credentials to mount a view.

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
        """Constructor for the SMBMountCredentials class"""

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


