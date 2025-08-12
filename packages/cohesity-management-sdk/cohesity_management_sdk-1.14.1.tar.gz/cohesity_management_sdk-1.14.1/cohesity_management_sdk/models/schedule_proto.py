# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.time_window
import cohesity_management_sdk.models.time_range_usecs
import cohesity_management_sdk.models.schedule_proto

class ScheduleProto(object):

    """Implementation of the 'ScheduleProto' model.

    Specifies the parameters for configuration of IPMI. This is only needed
    for physical clusters.

    Attributes:
        periodic_time_windows (list of TimeWindow): Specifies the time
            range within the days of the week. This field is non-empty iff
            type == kPeriodicTimeWindows.'
        timezone (string):Timezone of the user of this ScheduleProto. The
            timezones have unique names of the form "Area/Location".
        mtype (int): Specifies the type of schedule for this ScheduleProto.
        time_ranges (list of TimeRangeUsecs): Specifies the time ranges in
            usecs. This field is non-empty iff type == kCustomIntervals.'
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "periodic_time_windows":'periodicTimeWindows',
        "timezone":'timezone',
        "mtype":'type',
        "time_ranges":'timeRanges'
    }

    def __init__(self,
                 periodic_time_windows=None,
                 timezone=None,
                 mtype=None,
                 time_ranges=None):
        """Constructor for the ScheduleProto class"""

        # Initialize members of the class
        self.periodic_time_windows = periodic_time_windows
        self.timezone = timezone
        self.mtype = mtype
        self.time_ranges = time_ranges


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
        if dictionary.get("periodicTimeWindows") is not None:
            periodic_time_windows = list()
            for structure in dictionary.get('periodicTimeWindows'):
                periodic_time_windows.append(cohesity_management_sdk.models.time_window.TimeWindow.from_dictionary(structure))
        timezone = dictionary.get('timezone')
        mtype = dictionary.get('type')
        time_ranges = None
        if dictionary.get("timeRanges") is not None:
            time_ranges = list()
            for structure in dictionary.get('timeRanges'):
                time_ranges.append(cohesity_management_sdk.models.time_range_usecs.TimeRangeUsecs.from_dictionary(structure))

        # Return an object of this model
        return cls(periodic_time_windows,
                   timezone,
                   mtype,
                   time_ranges)


