# -*- coding: utf-8 -*-


class AzureTier(object):

    """Implementation of the 'AzureTier' model.

    Specifies the settings for a Azure tier.

    Attributes:
        move_after_unit (MoveAfterUnitEnum): Specifies the unit for moving the
            data from current tier to next tier. This unit will be a base unit
            for the 'moveAfter' field specified below.
        move_after (long|int): Specifies the time period after which the
            backup will be moved from current tier to next tier.
        tier_type (TierType1Enum): Specifies the Azure tier types.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "tier_type":'tierType',
        "move_after_unit":'moveAfterUnit',
        "move_after":'moveAfter'
    }

    def __init__(self,
                 tier_type=None,
                 move_after_unit=None,
                 move_after=None):
        """Constructor for the AzureTier class"""

        # Initialize members of the class
        self.move_after_unit = move_after_unit
        self.move_after = move_after
        self.tier_type = tier_type


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
        tier_type = dictionary.get('tierType')
        move_after_unit = dictionary.get('moveAfterUnit')
        move_after = dictionary.get('moveAfter')

        # Return an object of this model
        return cls(tier_type,
                   move_after_unit,
                   move_after)


