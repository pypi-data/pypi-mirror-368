# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.time_range_usecs
import cohesity_management_sdk.models_v2.time_window

class Schedule2(object):

    """Implementation of the 'Schedule2' model.

    Specifies a schedule for actions to be taken.

    Attributes:
        periodic_time_windows (list of TimeWindow): Specifies the time range within the days of the week.
        schedule_type (ScheduleTypeEnum): Specifies the type of schedule for this ScheduleProto.
        time_ranges (list of TimeRangeUsecs): Specifies the time ranges in usecs.
        timezone (string): Specifies the timezone of the user of this ScheduleProto. The
          timezones have unique names of the form 'Area/Location'.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "periodic_time_windows":'periodicTimeWindows',
        "schedule_type":'scheduleType',
        "time_ranges":'timeRanges',
        "timezone":'timezone'
    }

    def __init__(self,
                 periodic_time_windows=None,
                 schedule_type=None,
                 time_ranges=None,
                 timezone=None):
        """Constructor for the Schedule2 class"""

        # Initialize members of the class
        self.periodic_time_windows = periodic_time_windows
        self.schedule_type = schedule_type
        self.time_ranges = time_ranges
        self.timezone = timezone


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
        periodic_time_windows = None
        if dictionary.get('periodicTimeWindows') is not None:
            periodic_time_windows = list()
            for structure in dictionary.get('periodicTimeWindows'):
                periodic_time_windows.append(cohesity_management_sdk.models_v2.time_window.TimeWindow.from_dictionary(structure))
        schedule_type = dictionary.get('scheduleType')
        time_ranges = None
        if dictionary.get('timeRanges') is not None:
            time_ranges = list()
            for structure in dictionary.get('timeRanges'):
                time_ranges.append(cohesity_management_sdk.models_v2.time_range_usecs.TimeRangeUsecs.from_dictionary(structure))
        timezone = dictionary.get('timezone')

        # Return an object of this model
        return cls(periodic_time_windows, schedule_type, time_ranges, timezone)