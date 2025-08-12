# -*- coding: utf-8 -*-


class FlashbladeObjectProtectionParams(object):

    """Implementation of the 'FlashbladeObjectProtectionParams' model.

    Specifies the parameters which are specific to Flashblade object
    protection.

    Attributes:
        protocol (Protocol4Enum): Specifies the protocol of the NAS device
            being backed up.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protocol":'protocol'
    }

    def __init__(self,
                 protocol=None):
        """Constructor for the FlashbladeObjectProtectionParams class"""

        # Initialize members of the class
        self.protocol = protocol


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
        protocol = dictionary.get('protocol')

        # Return an object of this model
        return cls(protocol)


