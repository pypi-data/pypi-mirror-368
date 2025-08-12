# -*- coding: utf-8 -*-


class NetworkInterfaceType(object):

    """Implementation of the 'Network Interface Type' model.

    Type of a network interface.

    Attributes:
        network_interface_type (NetworkInterfaceType1Enum): Specifies the
            network interface type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "network_interface_type":'networkInterfaceType'
    }

    def __init__(self,
                 network_interface_type=None):
        """Constructor for the NetworkInterfaceType class"""

        # Initialize members of the class
        self.network_interface_type = network_interface_type


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
        network_interface_type = dictionary.get('networkInterfaceType')

        # Return an object of this model
        return cls(network_interface_type)


