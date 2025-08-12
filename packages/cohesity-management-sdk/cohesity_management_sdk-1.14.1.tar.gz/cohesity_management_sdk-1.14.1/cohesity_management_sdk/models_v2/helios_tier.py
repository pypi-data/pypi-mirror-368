# -*- coding: utf-8 -*-


class HeliosTier(object):

    """Implementation of the 'HeliosTier' model.

    Specifies the Helios Tier details.

    Attributes:
        mtype (Type31Enum): Specifies the tier type.
        is_default_tier (bool): Specifies whether the current tier will be the
            default tier for primary retention.
        unit (Unit11Enum): Specificies the time unit after which backup will
            be moved to next tier.
        move_after (long|int): Specifies the duration after which the backup
            will be moved to next tier.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type',
        "is_default_tier":'isDefaultTier',
        "unit":'unit',
        "move_after":'moveAfter'
    }

    def __init__(self,
                 mtype=None,
                 is_default_tier=None,
                 unit=None,
                 move_after=None):
        """Constructor for the HeliosTier class"""

        # Initialize members of the class
        self.mtype = mtype
        self.is_default_tier = is_default_tier
        self.unit = unit
        self.move_after = move_after


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
        mtype = dictionary.get('type')
        is_default_tier = dictionary.get('isDefaultTier')
        unit = dictionary.get('unit')
        move_after = dictionary.get('moveAfter')

        # Return an object of this model
        return cls(mtype,
                   is_default_tier,
                   unit,
                   move_after)


