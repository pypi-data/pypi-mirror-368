# -*- coding: utf-8 -*-


class ScheduleUnit(object):

    """Implementation of the 'ScheduleUnit' model.

    Schedule Units

    Attributes:
        schedule_unit (ScheduleUnit1Enum): Specifies the schedule unit.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "schedule_unit":'scheduleUnit'
    }

    def __init__(self,
                 schedule_unit=None):
        """Constructor for the ScheduleUnit class"""

        # Initialize members of the class
        self.schedule_unit = schedule_unit


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
        schedule_unit = dictionary.get('scheduleUnit')

        # Return an object of this model
        return cls(schedule_unit)


