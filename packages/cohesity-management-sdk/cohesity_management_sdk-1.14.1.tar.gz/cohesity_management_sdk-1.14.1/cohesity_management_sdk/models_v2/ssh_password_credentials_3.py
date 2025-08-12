# -*- coding: utf-8 -*-


class SshPasswordCredentials3(object):

    """Implementation of the 'SshPasswordCredentials3' model.

    SSH username + password required for reading configuration file. Either
    'sshPasswordCredentials' or 'sshPrivateKeyCredentials' are required.

    Attributes:
        password (string): SSH password.
        username (string): SSH username.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "password":'password',
        "username":'username'
    }

    def __init__(self,
                 password=None,
                 username=None):
        """Constructor for the SshPasswordCredentials3 class"""

        # Initialize members of the class
        self.password = password
        self.username = username


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
        password = dictionary.get('password')
        username = dictionary.get('username')

        # Return an object of this model
        return cls(password,
                   username)


