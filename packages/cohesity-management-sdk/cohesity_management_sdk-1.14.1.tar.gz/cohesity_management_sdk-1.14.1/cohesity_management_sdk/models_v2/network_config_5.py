# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.new_network_config

class NetworkConfig5(object):

    """Implementation of the 'NetworkConfig5' model.

    Specifies the networking configuration to be applied to the recovered
    VMs.

    Attributes:
        detach_network (bool): If this is set to true, then the network will
            be detached from the recovered VMs. All the other networking
            parameters set will be ignored if set to true. Default value is
            false.
        new_network_config (NewNetworkConfig): Specifies a new network
            configuration for the VM recovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "detach_network":'detachNetwork',
        "new_network_config":'newNetworkConfig'
    }

    def __init__(self,
                 detach_network=None,
                 new_network_config=None):
        """Constructor for the NetworkConfig5 class"""

        # Initialize members of the class
        self.detach_network = detach_network
        self.new_network_config = new_network_config


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
        new_network_config = cohesity_management_sdk.models_v2.new_network_config.NewNetworkConfig.from_dictionary(dictionary.get('newNetworkConfig')) if dictionary.get('newNetworkConfig') else None

        # Return an object of this model
        return cls(detach_network,
                   new_network_config)


