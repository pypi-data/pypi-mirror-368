# -*- coding: utf-8 -*-


class Credentials1(object):

    """Implementation of the 'Credentials1' model.

    Specifies credentials to access the Universal Data Adapter source. For
    e.g.: To perform backup and recovery tasks with Oracle Recovery Manager
    (RMAN), specify credentials for a user having 'SYSDBA' or 'SYSBACKUP'
    administrative privilege.

    Attributes:
        password (string): Specifies the password to access target entity.
        username (string): Specifies the username to access target entity.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "password":'password',
        "username":'username'
    }

    def __init__(self,
                 password=None,
                 username=None):
        """Constructor for the Credentials1 class"""

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


