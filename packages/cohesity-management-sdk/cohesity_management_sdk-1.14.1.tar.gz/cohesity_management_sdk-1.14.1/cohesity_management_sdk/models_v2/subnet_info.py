# -*- coding: utf-8 -*-


class SubnetInfo(object):

    """Implementation of the 'SubnetInfo' model.

    Subnet information.

    Attributes:
        subnet_ip (string): Subnet IP.
        netmask_bits (int): Subnet netmask bits.
        gateway (string): Gateway.
        subnet_ipv4_mask (string): Subnet ipv4 mask. This is used only for V4 subnet

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "subnet_ip":'subnetIp',
        "netmask_bits":'netmaskBits',
        "gateway":'gateway',
        "subnet_ipv4_mask":'subnetIpv4Mask'
    }

    def __init__(self,
                 subnet_ip=None,
                 netmask_bits=None,
                 gateway=None,
                 subnet_ipv4_mask=None):
        """Constructor for the SubnetInfo class"""

        # Initialize members of the class
        self.subnet_ip = subnet_ip
        self.netmask_bits = netmask_bits
        self.gateway = gateway
        self.subnet_ipv4_mask = subnet_ipv4_mask


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
        subnet_ip = dictionary.get('subnetIp')
        netmask_bits = dictionary.get('netmaskBits')
        gateway = dictionary.get('gateway')
        subnet_ipv4_mask = dictionary.get('subnetIpv4Mask')

        # Return an object of this model
        return cls(subnet_ip,
                   netmask_bits,
                   gateway,
                   subnet_ipv4_mask)