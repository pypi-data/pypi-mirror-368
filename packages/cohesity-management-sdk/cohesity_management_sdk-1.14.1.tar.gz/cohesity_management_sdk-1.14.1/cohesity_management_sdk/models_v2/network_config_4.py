# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.virtual_network
import cohesity_management_sdk.models_v2.subnet_2
import cohesity_management_sdk.models_v2.network_resource_group

class NetworkConfig4(object):

    """Implementation of the 'NetworkConfig4' model.

    Specifies the networking configuration to be applied to the recovered
    VMs.

    Attributes:
        virtual_network (VirtualNetwork): Specifies the Virtual Network.
        subnet (Subnet2): Specifies the subnet within the above virtual
            network.
        network_resource_group (NetworkResourceGroup): Specifies id of the
            resource group for the selected virtual network.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "virtual_network":'virtualNetwork',
        "subnet":'subnet',
        "network_resource_group":'networkResourceGroup'
    }

    def __init__(self,
                 virtual_network=None,
                 subnet=None,
                 network_resource_group=None):
        """Constructor for the NetworkConfig4 class"""

        # Initialize members of the class
        self.virtual_network = virtual_network
        self.subnet = subnet
        self.network_resource_group = network_resource_group


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
        virtual_network = cohesity_management_sdk.models_v2.virtual_network.VirtualNetwork.from_dictionary(dictionary.get('virtualNetwork')) if dictionary.get('virtualNetwork') else None
        subnet = cohesity_management_sdk.models_v2.subnet_2.Subnet2.from_dictionary(dictionary.get('subnet')) if dictionary.get('subnet') else None
        network_resource_group = cohesity_management_sdk.models_v2.network_resource_group.NetworkResourceGroup.from_dictionary(dictionary.get('networkResourceGroup')) if dictionary.get('networkResourceGroup') else None

        # Return an object of this model
        return cls(virtual_network,
                   subnet,
                   network_resource_group)


