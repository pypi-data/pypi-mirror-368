# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.time

class TimeWindow(object):

    """Implementation of the 'TimeWindow' model.

    TODO: type model description here.

    Attributes:
        day (int): If the day is not set, the time range applies to all days.
            various params required to establish a connection with a
            particular environment.
        end_time (Time): End time of the time range.
        start_time (Time): Starttime of the time range.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "day":'day',
        "end_time":'endTime',
        "start_time":'startTime'
    }

    def __init__(self,
                 day=None,
                 end_time=None,
                 start_time=None):
        """Constructor for the TimeWindow class"""

        # Initialize members of the class
        self.day = day
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
        day = dictionary.get('day')
        end_time = cohesity_management_sdk.models.time.Time.from_dictionary(dictionary.get('endTime')) if dictionary.get('endTime') else None
        start_time = cohesity_management_sdk.models.time.Time.from_dictionary(dictionary.get('startTime')) if dictionary.get('startTime') else None

        # Return an object of this model
        return cls(day,
                   end_time,
                   start_time)


