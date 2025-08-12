# -*- coding: utf-8 -*-


class MonthSchedule1(object):

    """Implementation of the 'Month Schedule1' model.

    Specifies settings that define a schedule for a Protection Group runs to
    on specific week and specific days of that week.

    Attributes:
        day_of_week (list of DayOfWeekEnum): Specifies a list of days of the
            week when to start Protection Group Runs. <br> Example: To run a
            Protection Group on every Monday and Tuesday, set the schedule
            with following values: <br>  unit: 'Weeks' <br>  dayOfWeek:
            ['Monday','Tuesday']
        week_of_month (WeekOfMonthEnum): Specifies the week of the month (such
            as 'Third') in a Monthly Schedule specified by unit field as
            'Months'. <br>This field is used in combination with 'dayOfWeek'
            to define the day in the month to start the Protection Group Run.
            <br> Example: if 'weekOfMonth' is set to 'Third' and day is set to
            'Monday', a backup is performed on the third Monday of every
            month.
        day_of_month (long|int): Specifies the exact date of the month (such as 18) in a Monthly
          Schedule specified by unit field as ''Years''. <br> Example: if ''dayOfMonth''
          is set to ''18'', a backup is performed on the 18th of every month.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "day_of_week":'dayOfWeek',
        "week_of_month":'weekOfMonth',
        "day_of_month":'dayOfMonth'
    }

    def __init__(self,
                 day_of_week=None,
                 week_of_month=None,
                 day_of_month=None):
        """Constructor for the MonthSchedule1 class"""

        # Initialize members of the class
        self.day_of_week = day_of_week
        self.week_of_month = week_of_month
        self.day_of_month = day_of_month


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
        week_of_month = dictionary.get('weekOfMonth')
        day_of_month = dictionary.get('dayOfMonth')

        # Return an object of this model
        return cls(
                   day_of_week,
                   week_of_month,
        day_of_month)