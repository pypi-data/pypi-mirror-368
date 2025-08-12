# -*- coding: utf-8 -*-


class NasProtocolType(object):

    """Implementation of the 'Nas Protocol type.' model.

    Nas Protocol type.

    Attributes:
        nas_protocol (NasProtocolEnum): Specifies Nas Protocol type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "nas_protocol":'nasProtocol'
    }

    def __init__(self,
                 nas_protocol=None):
        """Constructor for the NasProtocolType class"""

        # Initialize members of the class
        self.nas_protocol = nas_protocol


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
        nas_protocol = dictionary.get('nasProtocol')

        # Return an object of this model
        return cls(nas_protocol)


