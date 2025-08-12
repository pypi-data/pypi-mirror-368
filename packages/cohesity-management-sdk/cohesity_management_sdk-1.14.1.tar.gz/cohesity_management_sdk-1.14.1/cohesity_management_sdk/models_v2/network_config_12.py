# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.subnet_4

class NetworkConfig12(object):

    """Implementation of the 'NetworkConfig12' model.

    Specifies the networking configuration to be applied to the recovered
    VMs.

    Attributes:
        subnet (Subnet4): Specifies the subnet.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "subnet":'subnet'
    }

    def __init__(self,
                 subnet=None):
        """Constructor for the NetworkConfig12 class"""

        # Initialize members of the class
        self.subnet = subnet


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
        subnet = cohesity_management_sdk.models_v2.subnet_4.Subnet4.from_dictionary(dictionary.get('subnet')) if dictionary.get('subnet') else None

        # Return an object of this model
        return cls(subnet)


