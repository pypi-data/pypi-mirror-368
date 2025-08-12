# -*- coding: utf-8 -*-


class RecoverVmwareVMsOriginalSourceNetworkConfiguration(object):

    """Implementation of the 'Recover VMware VMs Original Source Network configuration.' model.

    Specifies the network config parameters to be applied for VMware VMs if
    recovering to original Source.

    Attributes:
        detach_network (bool): If this is set to true, then the network will
            be detached from the recovered VMs. All the other networking
            parameters set will be ignored if set to true. Default value is
            false.
        disable_network (bool): Specifies whether the attached network should
            be left in disabled state. Default is false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "detach_network":'detachNetwork',
        "disable_network":'disableNetwork'
    }

    def __init__(self,
                 detach_network=None,
                 disable_network=None):
        """Constructor for the RecoverVmwareVMsOriginalSourceNetworkConfiguration class"""

        # Initialize members of the class
        self.detach_network = detach_network
        self.disable_network = disable_network


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
        disable_network = dictionary.get('disableNetwork')

        # Return an object of this model
        return cls(detach_network,
                   disable_network)


