# -*- coding: utf-8 -*-


class TimeWindow(object):

    """Implementation of the 'TimeWindow' model.

    Specifies a a time range within a day.

    Attributes:
        day_of_the_week (DayOfTheWeekEnum): Specifies the week day.
        end_time (Time): Specifies the end time of this time range.
        start_time (Time): Specifies the start time of this time range.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "day_of_the_week":'dayOfTheWeek',
        "end_time":'endTime',
        "start_time":'startTime'
    }

    def __init__(self,
                 day_of_the_week=None,
                 end_time=None,
                 start_time=None):
        """Constructor for the TimeWindow class"""

        # Initialize members of the class
        self.day_of_the_week = day_of_the_week
        self.end_time = end_time
        self.start_time = start_time


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
        day_of_the_week = dictionary.get('dayOfTheWeek')
        end_time = dictionary.get('endTime')
        start_time = dictionary.get('startTime')

        # Return an object of this model
        return cls(day_of_the_week,
                   end_time,
                   start_time)