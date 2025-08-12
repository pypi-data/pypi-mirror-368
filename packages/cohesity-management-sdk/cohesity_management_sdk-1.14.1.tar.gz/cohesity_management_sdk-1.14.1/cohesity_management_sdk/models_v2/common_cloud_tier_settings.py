# -*- coding: utf-8 -*-


class CommonCloudTierSettings(object):

    """Implementation of the 'CommonCloudTierSettings' model.

    Specifies the common settings required for configuring cloud tiering.

    Attributes:
        move_after_unit (MoveAfterUnitEnum): Specifies the unit for moving the
            data from current tier to next tier. This unit will be a base unit
            for the 'moveAfter' field specified below.
        move_after (long|int): Specifies the time period after which the
            backup will be moved from current tier to next tier.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "move_after_unit":'moveAfterUnit',
        "move_after":'moveAfter'
    }

    def __init__(self,
                 move_after_unit=None,
                 move_after=None):
        """Constructor for the CommonCloudTierSettings class"""

        # Initialize members of the class
        self.move_after_unit = move_after_unit
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
        move_after_unit = dictionary.get('moveAfterUnit')
        move_after = dictionary.get('moveAfter')

        # Return an object of this model
        return cls(move_after_unit,
                   move_after)


