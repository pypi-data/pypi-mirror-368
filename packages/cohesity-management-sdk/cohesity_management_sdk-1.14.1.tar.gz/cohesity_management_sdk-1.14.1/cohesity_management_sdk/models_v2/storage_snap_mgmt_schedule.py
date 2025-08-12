# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.daily_schedule
import cohesity_management_sdk.models_v2.month_schedule
import cohesity_management_sdk.models_v2.week_schedule
import cohesity_management_sdk.models_v2.year_schedule_1


class StorageSnapMgmtSchedule(object):

    """Implementation of the 'StorageSnapMgmtSchedule' model.

    Specifies settings that defines how frequent Storage Snapshot Management
      backup will be performed for a Protection Group.

    Attributes:
        day_schedule (DailySchedule): Specifies the days Schedule for Protection Group to start runs
          after certain number of days.
        hour_schedule (DailySchedule): Specifies the days Schedule for Protection Group to start runs
          after certain number of hours.
        minute_schedule (DailySchedule): Specifies the days Schedule for Protection Group to start runs
          after certain number of minutes.
        month_schedule (MonthSchedule): Specifies the week Schedule for Protection Group to start runs
          on specific week in a month and specific days of that week.
        unit (Unit8Enum): Specifies how often to start new Protection Group Runs of a Protection
          Group. <br>'Minutes' specifies that Protection Group run starts periodically
          after certain number of minutes specified in 'frequency' field. <br>'Hours'
          specifies that Protection Group run starts periodically after certain number
          of hours specified in 'frequency' field
        week_schedule (WeekSchedule): Specifies the week Schedule for Protection Group to start runs
          on certain number of days in a week.
        year_schedule (YearSchedule): Specifies the year Schedule for Protection Group to start runs
          on specific day of that year.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "day_schedule":'daySchedule',
        "hour_schedule":'hourSchedule',
        "minute_schedule":'minuteSchedule',
        "month_schedule":'monthSchedule',
        "unit":'unit',
        "week_schedule":'weekSchedule',
        "year_schedule":'yearSchedule'

    }

    def __init__(self,
                 day_schedule=None,
                 hour_schedule=None,
                 minute_schedule=None,
                 month_schedule=None,
                 unit=None,
                 week_schedule=None,
                 year_schedule=None
                 ):
        """Constructor for the StorageSnapMgmtSchedule class"""

        # Initialize members of the class
        self.day_schedule = day_schedule
        self.hour_schedule = hour_schedule
        self.minute_schedule = minute_schedule
        self.month_schedule = month_schedule
        self.unit = unit
        self.week_schedule = week_schedule
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
        day_schedule = cohesity_management_sdk.models_v2.daily_schedule.DailySchedule.from_dictionary(dictionary.get('daySchedule')) if dictionary.get('daySchedule') else None
        hour_schedule = cohesity_management_sdk.models_v2.daily_schedule.DailySchedule.from_dictionary(dictionary.get('hourSchedule')) if dictionary.get('hourSchedule') else None
        minute_schedule = cohesity_management_sdk.models_v2.daily_schedule.DailySchedule.from_dictionary(dictionary.get('minuteSchedule')) if dictionary.get('minuteSchedule') else None
        month_schedule = cohesity_management_sdk.models_v2.month_schedule.MonthSchedule.from_dictionary(dictionary.get('monthSchedule')) if dictionary.get('monthSchedule') else None
        unit = dictionary.get('unit')
        week_schedule = cohesity_management_sdk.models_v2.week_schedule.WeekSchedule.from_dictionary(dictionary.get('weekSchedule')) if dictionary.get('weekSchedule') else None
        year_schedule = cohesity_management_sdk.models_v2.year_schedule_1.YearSchedule1.from_dictionary(dictionary.get('yearSchedule')) if dictionary.get('yearSchedule') else None


        # Return an object of this model
        return cls(day_schedule,
                   hour_schedule,
                   minute_schedule,
                   month_schedule,
                   unit,
                   week_schedule,
                   year_schedule)