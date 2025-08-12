# -*- coding: utf-8 -*-


class FlashbladeProtocolType(object):

    """Implementation of the 'Flashblade Protocol type.' model.

    Flashblade Protocol type.

    Attributes:
        flashblade_protocol (FlashbladeProtocolEnum): Specifies Flashblade
            Protocol type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "flashblade_protocol":'flashbladeProtocol'
    }

    def __init__(self,
                 flashblade_protocol=None):
        """Constructor for the FlashbladeProtocolType class"""

        # Initialize members of the class
        self.flashblade_protocol = flashblade_protocol


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
        flashblade_protocol = dictionary.get('flashbladeProtocol')

        # Return an object of this model
        return cls(flashblade_protocol)


