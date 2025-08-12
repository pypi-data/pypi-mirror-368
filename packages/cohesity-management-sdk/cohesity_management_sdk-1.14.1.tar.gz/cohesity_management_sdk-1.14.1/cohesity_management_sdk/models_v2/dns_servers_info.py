# -*- coding: utf-8 -*-


class DnsServersInfo(object):

    """Implementation of the 'DnsServersInfo' model.

    List of DNS servers in cluster.

    Attributes:
        dns_servers (list of string): List of DNS servers in cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "dns_servers":'dnsServers'
    }

    def __init__(self,
                 dns_servers=None):
        """Constructor for the DnsServersInfo class"""

        # Initialize members of the class
        self.dns_servers = dns_servers


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
        dns_servers = dictionary.get('dnsServers')

        # Return an object of this model
        return cls(dns_servers)


