# -*- coding: utf-8 -*-


class ResourceEndpoint(object):

    """Implementation of the 'ResourceEndpoint' model.

    Specifies the details about the resource endpoint.

    Attributes:
        fqdn (string): Specifies the fqdn of this endpoint.
        ipv_4_addr (string): Specifies the ipv4 address of this endpoint.
        ipv_6_addr (string): Specifies the ipv6 address of this endpoint.
        subnet_ip_4_addr (string): Specifies the subnet Ip4 address of this
            endpoint.
        preferred_address (string): Specifies the preferred address to use for
            connecting.
        is_preferred_endpoint (bool): Whether to use this endpoint to
            connect.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "fqdn":'fqdn',
        "ipv_4_addr":'ipv4addr',
        "ipv_6_addr":'ipv6addr',
        "subnet_ip_4_addr":'subnetIp4addr',
        "preferred_address":'preferredAddress',
        "is_preferred_endpoint":'isPreferredEndpoint'
    }

    def __init__(self,
                 fqdn=None,
                 ipv_4_addr=None,
                 ipv_6_addr=None,
                 subnet_ip_4_addr=None,
                 preferred_address=None,
                 is_preferred_endpoint=None):
        """Constructor for the ResourceEndpoint class"""

        # Initialize members of the class
        self.fqdn = fqdn
        self.ipv_4_addr = ipv_4_addr
        self.ipv_6_addr = ipv_6_addr
        self.subnet_ip_4_addr = subnet_ip_4_addr
        self.preferred_address = preferred_address
        self.is_preferred_endpoint = is_preferred_endpoint


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
        fqdn = dictionary.get('fqdn')
        ipv_4_addr = dictionary.get('ipv4addr')
        ipv_6_addr = dictionary.get('ipv6addr')
        subnet_ip_4_addr = dictionary.get('subnetIp4addr')
        preferred_address = dictionary.get('preferredAddress')
        is_preferred_endpoint = dictionary.get('isPreferredEndpoint')

        # Return an object of this model
        return cls(fqdn,
                   ipv_4_addr,
                   ipv_6_addr,
                   subnet_ip_4_addr,
                   preferred_address,
                   is_preferred_endpoint)


