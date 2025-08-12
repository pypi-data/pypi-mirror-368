# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class ClusterNetworkingEndpoint(object):

    """Implementation of the 'ClusterNetworkingEndpoint' model.

    Specifies information about end point.

    Attributes:
        fqdn (string): The Fully Qualified Domain Name.
        ipv_4_addr (string): The IPv4 address.
        ipv_6_addr (string): The IPv6 address.
        is_preferred_endpoint (bool): Specifies if this endpoint is preferred
            or not.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "fqdn":'fqdn',
        "ipv_4_addr":'ipv4Addr',
        "ipv_6_addr":'ipv6Addr',
        "is_preferred_endpoint": 'isPreferredEndpoint'
    }

    def __init__(self,
                 fqdn=None,
                 ipv_4_addr=None,
                 ipv_6_addr=None,
                 is_preferred_endpoint=None):
        """Constructor for the ClusterNetworkingEndpoint class"""

        # Initialize members of the class
        self.fqdn = fqdn
        self.ipv_4_addr = ipv_4_addr
        self.ipv_6_addr = ipv_6_addr
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
        ipv_4_addr = dictionary.get('ipv4Addr')
        ipv_6_addr = dictionary.get('ipv6Addr')
        is_preferred_endpoint = dictionary.get('isPreferredEndpoint')

        # Return an object of this model
        return cls(fqdn,
                   ipv_4_addr,
                   ipv_6_addr,
                   is_preferred_endpoint)


