# -*- coding: utf-8 -*-


class NetappProtocolType(object):

    """Implementation of the 'Netapp Protocol type.' model.

    Netapp Protocol type.

    Attributes:
        netapp_protocol (NetappProtocolEnum): Specifies Netapp Protocol type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "netapp_protocol":'netappProtocol'
    }

    def __init__(self,
                 netapp_protocol=None):
        """Constructor for the NetappProtocolType class"""

        # Initialize members of the class
        self.netapp_protocol = netapp_protocol


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
        netapp_protocol = dictionary.get('netappProtocol')

        # Return an object of this model
        return cls(netapp_protocol)


