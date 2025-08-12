# -*- coding: utf-8 -*-


class ClusterNetworkConfig1(object):

    """Implementation of the 'Cluster Network Config.1' model.

    Specifies all of the parameters needed for network configuration of the
    new Cluster using DHCP.

    Attributes:
        gateway (string): Specifies the gateway of the new cluster network.
        subnet_ip (string): Specifies the ip subnet ip of the cluster
            network.
        subnet_mask (string): Specifies the ip subnet mask of the cluster
            network.
        dns_servers (list of string): Specifies the list of Dns Servers new
            cluster should be configured with.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "dns_servers":'dnsServers',
        "gateway":'gateway',
        "subnet_ip":'subnetIp',
        "subnet_mask":'subnetMask'
    }

    def __init__(self,
                 dns_servers=None,
                 gateway=None,
                 subnet_ip=None,
                 subnet_mask=None):
        """Constructor for the ClusterNetworkConfig1 class"""

        # Initialize members of the class
        self.gateway = gateway
        self.subnet_ip = subnet_ip
        self.subnet_mask = subnet_mask
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
        gateway = dictionary.get('gateway')
        subnet_ip = dictionary.get('subnetIp')
        subnet_mask = dictionary.get('subnetMask')

        # Return an object of this model
        return cls(dns_servers,
                   gateway,
                   subnet_ip,
                   subnet_mask)


