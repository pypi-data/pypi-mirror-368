# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.new_network_config_1

class RecoverKVMVMsNewSourceNetworkConfiguration(object):

    """Implementation of the 'Recover KVM VMs New Source Network configuration.' model.

    Specifies the network config parameters to be applied for KVM VMs if
    recovering to new Source.

    Attributes:
        detach_network (bool): If this is set to true, then the network will
            be detached from the recovered VMs. All the other networking
            parameters set will be ignored if set to true. Default value is
            false.
        new_network_config (NewNetworkConfig1): Specifies the new network
            configuration of the Kvm recovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "detach_network":'detachNetwork',
        "new_network_config":'newNetworkConfig'
    }

    def __init__(self,
                 detach_network=None,
                 new_network_config=None):
        """Constructor for the RecoverKVMVMsNewSourceNetworkConfiguration class"""

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
        new_network_config = cohesity_management_sdk.models_v2.new_network_config_1.NewNetworkConfig1.from_dictionary(dictionary.get('newNetworkConfig')) if dictionary.get('newNetworkConfig') else None

        # Return an object of this model
        return cls(detach_network,
                   new_network_config)


