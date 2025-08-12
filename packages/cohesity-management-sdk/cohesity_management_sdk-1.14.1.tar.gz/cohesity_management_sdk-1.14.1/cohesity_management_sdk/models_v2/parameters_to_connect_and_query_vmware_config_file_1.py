# -*- coding: utf-8 -*-


class ParametersToConnectAndQueryVmwareConfigFile1(object):

    """Implementation of the 'Parameters to connect and query VMware config file.1' model.

    Specifies the parameters to connect to a seed node and fetch information
    from its config file.

    Attributes:
        host (string): IP or hostname of the source.
        username (string): Specifies the username to access target entity.
        password (string): Specifies the password to access target entity.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "host":'host',
        "username":'username',
        "password":'password'
    }

    def __init__(self,
                 host=None,
                 username=None,
                 password=None):
        """Constructor for the ParametersToConnectAndQueryVmwareConfigFile1 class"""

        # Initialize members of the class
        self.host = host
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
        host = dictionary.get('host')
        username = dictionary.get('username')
        password = dictionary.get('password')

        # Return an object of this model
        return cls(host,
                   username,
                   password)


