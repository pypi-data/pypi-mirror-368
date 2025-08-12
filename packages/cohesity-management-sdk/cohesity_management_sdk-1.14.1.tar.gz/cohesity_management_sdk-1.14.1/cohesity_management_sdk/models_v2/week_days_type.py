# -*- coding: utf-8 -*-


class WeekDaysType(object):

    """Implementation of the 'Week Days type.' model.

    Week Days type.

    Attributes:
        week_days (WeekDaysEnum): Specifies Week Days type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "week_days":'weekDays'
    }

    def __init__(self,
                 week_days=None):
        """Constructor for the WeekDaysType class"""

        # Initialize members of the class
        self.week_days = week_days


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
        week_days = dictionary.get('weekDays')

        # Return an object of this model
        return cls(week_days)


