# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.network_port_group

class RecoverAcropolisVMsNetworkConfiguration(object):

    """Implementation of the 'Recover Acropolis VMs network configuration.' model.

    Specifies the network config parameters to applied for Acropolis VMs.

    Attributes:
        detach_network (bool): If this is set to true, then the network will
            be detached from the recovered VMs. All the other networking
            parameters set will be ignored if set to true. Default value is
            false.
        network_port_group (NetworkPortGroup): Specifies the network port
            group (i.e, either a standard switch port group or a distributed
            port group) that will attached to the recovered Object. This
            parameter is mandatory if detach network is specified as false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "detach_network":'detachNetwork',
        "network_port_group":'networkPortGroup'
    }

    def __init__(self,
                 detach_network=None,
                 network_port_group=None):
        """Constructor for the RecoverAcropolisVMsNetworkConfiguration class"""

        # Initialize members of the class
        self.detach_network = detach_network
        self.network_port_group = network_port_group


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
        detach_network = dictionary.get('detachNetwork')
        network_port_group = cohesity_management_sdk.models_v2.network_port_group.NetworkPortGroup.from_dictionary(dictionary.get('networkPortGroup')) if dictionary.get('networkPortGroup') else None

        # Return an object of this model
        return cls(detach_network,
                   network_port_group)


