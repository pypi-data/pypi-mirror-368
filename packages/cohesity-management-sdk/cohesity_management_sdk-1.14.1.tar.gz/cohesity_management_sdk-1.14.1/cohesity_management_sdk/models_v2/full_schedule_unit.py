# -*- coding: utf-8 -*-


class FullScheduleUnit(object):

    """Implementation of the 'FullScheduleUnit' model.

    Full Schedule Units

    Attributes:
        full_schedule_unit (FullScheduleUnit1Enum): Specifies the full
            schedule unit (including ProtectOnce policy).

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "full_schedule_unit":'fullScheduleUnit'
    }

    def __init__(self,
                 full_schedule_unit=None):
        """Constructor for the FullScheduleUnit class"""

        # Initialize members of the class
        self.full_schedule_unit = full_schedule_unit


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
        full_schedule_unit = dictionary.get('fullScheduleUnit')

        # Return an object of this model
        return cls(full_schedule_unit)


