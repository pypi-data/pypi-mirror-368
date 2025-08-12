# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.subnet_5

class LoadBalancerConfig(object):

    """Implementation of the 'LoadBalancerConfig' model.

    Load balancer VIP config for OneHelios cluster.

    Attributes:
        gateway (string): Specifies gateway.
        host_name (string): Specifies host name of the Helios endpoint.
        subnet (SubnetDefinition): Specifies subnet.
        virtual_ip_vec (list of string): Specifies list of Virtual IP Addresses.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "gateway":'gateway',
        "host_name":'hostName',
        "subnet":'subnet',
        "virtual_ip_vec":'virtualIpVec'
    }

    def __init__(self,
                 gateway=None,
                 host_name=None,
                 subnet=None,
                 virtual_ip_vec=None):
        """Constructor for the LoadBalancerConfig class"""

        # Initialize members of the class
        self.gateway = gateway
        self.host_name = host_name
        self.subnet = subnet
        self.virtual_ip_vec = virtual_ip_vec


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
        gateway = dictionary.get('gateway')
        host_name = dictionary.get('hostName')
        subnet = cohesity_management_sdk.models_v2.subnet_5.Subnet5.from_dictionary(dictionary.get('subnet'))
        virtual_ip_vec = dictionary.get('virtualIpVec')

        # Return an object of this model
        return cls(gateway, host_name, subnet, virtual_ip_vec)