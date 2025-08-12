# -*- coding: utf-8 -*-


class WeekSchedule(object):

    """Implementation of the 'Week Schedule' model.

    Specifies settings that define a schedule for a Protection Group runs to
    start on certain days of week.

    Attributes:
        day_of_week (list of DayOfWeekEnum): Specifies a list of days of the
            week when to start Protection Group Runs. <br> Example: To run a
            Protection Group on every Monday and Tuesday, set the schedule
            with following values: <br>  unit: 'Weeks' <br>  dayOfWeek:
            ['Monday','Tuesday']

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "day_of_week":'dayOfWeek'
    }

    def __init__(self,
                 day_of_week=None):
        """Constructor for the WeekSchedule class"""

        # Initialize members of the class
        self.day_of_week = day_of_week


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
        day_of_week = dictionary.get('dayOfWeek')

        # Return an object of this model
        return cls(day_of_week)


