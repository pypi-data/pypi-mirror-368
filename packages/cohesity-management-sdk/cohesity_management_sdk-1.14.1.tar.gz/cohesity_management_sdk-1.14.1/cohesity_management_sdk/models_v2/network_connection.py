# -*- coding: utf-8 -*-


class NetworkConnection(object):

    """Implementation of the 'Network Connection.' model.

    Specify the network connection information.

    Attributes:
        domain_name (string): Specifies the domain name of the network
            connection.
        network_gateway (string): Specifies the network Gateway of the network
            connection.
        dns (string): Specifies the DNS Server of the network connection.
        ntp (string): Specifies the NTP Server of the network connection.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "domain_name":'domainName',
        "network_gateway":'networkGateway',
        "dns":'dns',
        "ntp":'ntp'
    }

    def __init__(self,
                 domain_name=None,
                 network_gateway=None,
                 dns=None,
                 ntp=None):
        """Constructor for the NetworkConnection class"""

        # Initialize members of the class
        self.domain_name = domain_name
        self.network_gateway = network_gateway
        self.dns = dns
        self.ntp = ntp


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
        domain_name = dictionary.get('domainName')
        network_gateway = dictionary.get('networkGateway')
        dns = dictionary.get('dns')
        ntp = dictionary.get('ntp')

        # Return an object of this model
        return cls(domain_name,
                   network_gateway,
                   dns,
                   ntp)


