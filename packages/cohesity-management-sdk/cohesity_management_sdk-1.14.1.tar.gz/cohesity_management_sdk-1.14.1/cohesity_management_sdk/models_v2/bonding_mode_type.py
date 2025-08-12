# -*- coding: utf-8 -*-


class BondingModeType(object):

    """Implementation of the 'Bonding Mode Type' model.

    Type of bonding mode.

    Attributes:
        bonding_mode_type (BondingModeType1Enum): Specifies the bonding mode
            type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "bonding_mode_type":'bondingModeType'
    }

    def __init__(self,
                 bonding_mode_type=None):
        """Constructor for the BondingModeType class"""

        # Initialize members of the class
        self.bonding_mode_type = bonding_mode_type


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
        bonding_mode_type = dictionary.get('bondingModeType')

        # Return an object of this model
        return cls(bonding_mode_type)


