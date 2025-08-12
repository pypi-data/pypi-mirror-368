# -*- coding: utf-8 -*-


class ProtocolAccessLevel(object):

    """Implementation of the 'Protocol access level' model.

    Protocol access level

    Attributes:
        protocol_access_level (ProtocolAccessLevel1Enum): Specifies the level
            of access for any protocol.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protocol_access_level":'protocolAccessLevel'
    }

    def __init__(self,
                 protocol_access_level=None):
        """Constructor for the ProtocolAccessLevel class"""

        # Initialize members of the class
        self.protocol_access_level = protocol_access_level


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
        protocol_access_level = dictionary.get('protocolAccessLevel')

        # Return an object of this model
        return cls(protocol_access_level)


