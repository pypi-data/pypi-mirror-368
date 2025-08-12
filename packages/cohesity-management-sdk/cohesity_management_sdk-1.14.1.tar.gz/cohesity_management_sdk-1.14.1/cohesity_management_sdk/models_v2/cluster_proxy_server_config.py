# -*- coding: utf-8 -*-


class ClusterProxyServerConfig(object):

    """Implementation of the 'Cluster Proxy Server Config.' model.

    Specifies the parameters of the proxy server to be used for external
    traffic.

    Attributes:
        ip (string): Specifies the IP address of the proxy server.
        is_disabled (bool): Disable proxy is used to turn the proxy on and off.
        name (string): Specifies the unique name of the proxy server.
        password (string): Specifies the password for the proxy.
        port (int): Specifies the port on which the server is listening.
        username (string): Specifies the username for the proxy.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "ip":'ip',
        "is_disabled":'isDisabled',
        "name":'name',
        "password":'password',
        "port":'port',
        "username":'username'
    }

    def __init__(self,
                 ip=None,
                 is_disabled=None,
                 name=None,
                 password=None,
                 port=None,
                 username=None,):
        """Constructor for the ClusterProxyServerConfig class"""

        # Initialize members of the class
        self.ip = ip
        self.is_disabled = is_disabled
        self.name = name
        self.password = password
        self.port = port
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
        ip = dictionary.get('ip')
        is_disabled = dictionary.get('isDisabled')
        name = dictionary.get('name')
        password = dictionary.get('password')
        port = dictionary.get('port')
        username = dictionary.get('username')

        # Return an object of this model
        return cls(ip,
                   is_disabled,
                   name,
                   password,
                   port,
                   username,)