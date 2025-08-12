# -*- coding: utf-8 -*-


class KeystoneAdminParams(object):

    """Implementation of the 'KeystoneAdminParams' model.

    Specifies administrator credentials of a Keystone.

    Attributes:
        domain (string): Specifies the administrator domain name.
        username (string): Specifies the username of Keystone administrator.
        password (string): Specifies the password of Keystone administrator.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "domain":'domain',
        "username":'username',
        "password":'password'
    }

    def __init__(self,
                 domain=None,
                 username=None,
                 password=None):
        """Constructor for the KeystoneAdminParams class"""

        # Initialize members of the class
        self.domain = domain
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
        domain = dictionary.get('domain')
        username = dictionary.get('username')
        password = dictionary.get('password')

        # Return an object of this model
        return cls(domain,
                   username,
                   password)


