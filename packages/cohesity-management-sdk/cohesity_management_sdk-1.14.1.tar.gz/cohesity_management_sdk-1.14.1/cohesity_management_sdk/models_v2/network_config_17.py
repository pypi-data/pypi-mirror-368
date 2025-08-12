# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.virtual_switch

class NetworkConfig17(object):

    """Implementation of the 'NetworkConfig17' model.

    Specifies the networking configuration to be applied to the recovered
    VMs.

    Attributes:
        detach_network (bool): If this is set to true, then the network will
            be detached from the recovered VMs. All the other networking
            parameters set will be ignored if set to true. Default value is
            false.
        virtual_switch (VirtualSwitch): Specifies the virtual switch that will
            attached to all the network interfaces of the VMs being recovered.
            This parameter is mandatory if detach network is specified as
            false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "detach_network":'detachNetwork',
        "virtual_switch":'virtualSwitch'
    }

    def __init__(self,
                 detach_network=None,
                 virtual_switch=None):
        """Constructor for the NetworkConfig17 class"""

        # Initialize members of the class
        self.detach_network = detach_network
        self.virtual_switch = virtual_switch


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
        virtual_switch = cohesity_management_sdk.models_v2.virtual_switch.VirtualSwitch.from_dictionary(dictionary.get('virtualSwitch')) if dictionary.get('virtualSwitch') else None

        # Return an object of this model
        return cls(detach_network,
                   virtual_switch)


