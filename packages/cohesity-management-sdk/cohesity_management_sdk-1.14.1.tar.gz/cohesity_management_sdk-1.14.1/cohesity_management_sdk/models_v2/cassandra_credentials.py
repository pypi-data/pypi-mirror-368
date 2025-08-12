# -*- coding: utf-8 -*-


class CassandraCredentials(object):

    """Implementation of the 'CassandraCredentials' model.

    Cassandra Credentials for this cluster.

    Attributes:
        password (string): Cassandra password.
        username (string): Cassandra username.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "password":'password',
        "username":'username'
    }

    def __init__(self,
                 password=None,
                 username=None):
        """Constructor for the CassandraCredentials class"""

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


