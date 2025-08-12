# -*- coding: utf-8 -*-


class ConnectionSubnet(object):

    """Implementation of the 'Connection Subnet.' model.

    Specify the subnet used in connection.

    Attributes:
        ip (string): Specifies the IP address part of the CIDR notation.
        mask_bits (int): Specifies the number of set bits in the subnet mask.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "ip":'ip',
        "mask_bits":'maskBits'
    }

    def __init__(self,
                 ip=None,
                 mask_bits=None):
        """Constructor for the ConnectionSubnet class"""

        # Initialize members of the class
        self.ip = ip
        self.mask_bits = mask_bits


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
        ip = dictionary.get('ip')
        mask_bits = dictionary.get('maskBits')

        # Return an object of this model
        return cls(ip,
                   mask_bits)


