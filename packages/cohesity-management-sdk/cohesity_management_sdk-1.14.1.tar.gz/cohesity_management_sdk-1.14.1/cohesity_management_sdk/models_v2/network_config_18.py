# -*- coding: utf-8 -*-


class NetworkConfig18(object):

    """Implementation of the 'NetworkConfig18' model.

    Specifies the networking configuration to be applied to the recovered
    VMs.

    Attributes:
        detach_network (bool): If this is set to true, then the network will
            be detached from the recovered VMs. Default value is false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "detach_network":'detachNetwork'
    }

    def __init__(self,
                 detach_network=None):
        """Constructor for the NetworkConfig18 class"""

        # Initialize members of the class
        self.detach_network = detach_network


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

        # Return an object of this model
        return cls(detach_network)


