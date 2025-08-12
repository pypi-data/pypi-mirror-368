# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.daily_schedule
import cohesity_management_sdk.models_v2.week_schedule
import cohesity_management_sdk.models_v2.month_schedule
import cohesity_management_sdk.models_v2.time_of_day

class DataMigrationSchedule(object):

    """Implementation of the 'DataMigrationSchedule' model.

    Specifies the Data Migration schedule.

    Attributes:
        unit (Unit8Enum): Specifies how often to migrate data from source to
            target
        day_schedule (DailySchedule): Specifies settings that define a
            schedule for a Protection Group runs to start after certain number
            of days.
        week_schedule (WeekSchedule): Specifies settings that define a
            schedule for a Protection Group runs to start on certain days of
            week.
        month_schedule (MonthSchedule): Specifies settings that define a
            schedule for a Protection Group runs to on specific week and
            specific days of that week.
        start_time (TimeOfDay): Specifies the time of day. Used for scheduling
            purposes.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "unit":'unit',
        "day_schedule":'daySchedule',
        "week_schedule":'weekSchedule',
        "month_schedule":'monthSchedule',
        "start_time":'startTime'
    }

    def __init__(self,
                 unit=None,
                 day_schedule=None,
                 week_schedule=None,
                 month_schedule=None,
                 start_time=None):
        """Constructor for the DataMigrationSchedule class"""

        # Initialize members of the class
        self.unit = unit
        self.day_schedule = day_schedule
        self.week_schedule = week_schedule
        self.month_schedule = month_schedule
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
        unit = dictionary.get('unit')
        day_schedule = cohesity_management_sdk.models_v2.daily_schedule.DailySchedule.from_dictionary(dictionary.get('daySchedule')) if dictionary.get('daySchedule') else None
        week_schedule = cohesity_management_sdk.models_v2.week_schedule.WeekSchedule.from_dictionary(dictionary.get('weekSchedule')) if dictionary.get('weekSchedule') else None
        month_schedule = cohesity_management_sdk.models_v2.month_schedule.MonthSchedule.from_dictionary(dictionary.get('monthSchedule')) if dictionary.get('monthSchedule') else None
        start_time = cohesity_management_sdk.models_v2.time_of_day.TimeOfDay.from_dictionary(dictionary.get('startTime')) if dictionary.get('startTime') else None

        # Return an object of this model
        return cls(unit,
                   day_schedule,
                   week_schedule,
                   month_schedule,
                   start_time)


