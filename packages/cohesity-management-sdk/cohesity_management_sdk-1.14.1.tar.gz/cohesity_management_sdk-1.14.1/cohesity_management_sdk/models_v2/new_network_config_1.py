# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.network_port_group
import cohesity_management_sdk.models_v2.vnic_profile

class NewNetworkConfig1(object):

    """Implementation of the 'NewNetworkConfig1' model.

    Specifies the new network configuration of the Kvm recovery.

    Attributes:
        network_port_group (NetworkPortGroup): Specifies the network port
            group (i.e, either a standard switch port group or a distributed
            port group) that will attached to the recovered Object. This
            parameter is mandatory if detach network is specified as false.
        vnic_profile (VnicProfile): Specifies VNic profile that will be
            attached to the restored object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "network_port_group":'networkPortGroup',
        "vnic_profile":'vnicProfile'
    }

    def __init__(self,
                 network_port_group=None,
                 vnic_profile=None):
        """Constructor for the NewNetworkConfig1 class"""

        # Initialize members of the class
        self.network_port_group = network_port_group
        self.vnic_profile = vnic_profile


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
        network_port_group = cohesity_management_sdk.models_v2.network_port_group.NetworkPortGroup.from_dictionary(dictionary.get('networkPortGroup')) if dictionary.get('networkPortGroup') else None
        vnic_profile = cohesity_management_sdk.models_v2.vnic_profile.VnicProfile.from_dictionary(dictionary.get('vnicProfile')) if dictionary.get('vnicProfile') else None

        # Return an object of this model
        return cls(network_port_group,
                   vnic_profile)


