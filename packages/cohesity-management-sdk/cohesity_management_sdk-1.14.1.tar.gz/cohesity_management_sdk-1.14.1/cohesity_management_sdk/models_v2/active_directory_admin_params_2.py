# -*- coding: utf-8 -*-


class ActiveDirectoryAdminParams2(object):

    """Implementation of the 'ActiveDirectoryAdminParams2' model.

    Specifies the params of a user with administrative privilege of this
    Active Directory. This field is mandatory if machine accounts are
    updated.

    Attributes:
        username (string): Specifies the user name.
        password (string): Specifies the password of the user.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "username":'username',
        "password":'password'
    }

    def __init__(self,
                 username=None,
                 password=None):
        """Constructor for the ActiveDirectoryAdminParams2 class"""

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


