# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.daily_schedule
import cohesity_management_sdk.models_v2.week_schedule
import cohesity_management_sdk.models_v2.month_schedule
import cohesity_management_sdk.models_v2.year_schedule_1

class BmrSchedule(object):

    """Implementation of the 'Bmr Schedule' model.

    Specifies settings that defines how frequent bmr backup will be performed
    for a Protection Group.

    Attributes:
        unit (Unit6Enum): Specifies how often to start new runs of a
            Protection Group. <br>'Weeks' specifies that new Protection Group
            runs start weekly on certain days specified using 'dayOfWeek'
            field. <br>'Months' specifies that new Protection Group runs start
            monthly on certain day of specific week.
        day_schedule (DailySchedule): Specifies settings that define a
            schedule for a Protection Group runs to start after certain number
            of days.
        week_schedule (WeekSchedule): Specifies settings that define a
            schedule for a Protection Group runs to start on certain days of
            week.
        month_schedule (MonthSchedule): Specifies settings that define a
            schedule for a Protection Group runs to on specific week and
            specific days of that week.
        year_schedule (YearSchedule): Specifies the year Schedule for Protection Group to start runs
          on specific day of that year.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "unit":'unit',
        "day_schedule":'daySchedule',
        "week_schedule":'weekSchedule',
        "month_schedule":'monthSchedule',
        "year_schedule":'yearSchedule'
    }

    def __init__(self,
                 unit=None,
                 day_schedule=None,
                 week_schedule=None,
                 month_schedule=None,
                 year_schedule=None):
        """Constructor for the BmrSchedule class"""

        # Initialize members of the class
        self.unit = unit
        self.day_schedule = day_schedule
        self.week_schedule = week_schedule
        self.month_schedule = month_schedule
        self.year_schedule = year_schedule


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
        unit = dictionary.get('unit')
        day_schedule = cohesity_management_sdk.models_v2.daily_schedule.DailySchedule.from_dictionary(dictionary.get('daySchedule')) if dictionary.get('daySchedule') else None
        week_schedule = cohesity_management_sdk.models_v2.week_schedule.WeekSchedule.from_dictionary(dictionary.get('weekSchedule')) if dictionary.get('weekSchedule') else None
        month_schedule = cohesity_management_sdk.models_v2.month_schedule.MonthSchedule.from_dictionary(dictionary.get('monthSchedule')) if dictionary.get('monthSchedule') else None
        year_schedule = cohesity_management_sdk.models_v2.year_schedule_1.YearSchedule1.from_dictionary(dictionary.get('yearSchedule')) if dictionary.get('yearSchedule') else None

        # Return an object of this model
        return cls(unit,
                   day_schedule,
                   week_schedule,
                   month_schedule,
                   year_schedule)