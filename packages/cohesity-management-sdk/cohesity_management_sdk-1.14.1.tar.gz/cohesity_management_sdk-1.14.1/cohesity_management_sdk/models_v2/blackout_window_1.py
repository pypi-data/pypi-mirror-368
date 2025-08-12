# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.time_of_day

class BlackoutWindow1(object):

    """Implementation of the 'Blackout Window1' model.

    List of Blackout Windows. If specified, this field defines blackout
    periods when backups are not triggered..

    Attributes:
        day (DayEnum): Specifies a day in the week when no new Protection
            Group Runs should be started such as 'Sunday'. If not set, the
            time range applies to all days. Specifies a day in a week such as
            'Sunday', 'Monday', etc.
        start_time (TimeOfDay): Specifies the time of day. Used for scheduling
            purposes.
        end_time (TimeOfDay): Specifies the time of day. Used for scheduling
            purposes.
        config_id (string): Specifies the unique identifier for the blackout
            getting added. This field should only be set if policy is getting
            updated.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "day":'day',
        "start_time":'startTime',
        "end_time":'endTime',
        "config_id":'configId'
    }

    def __init__(self,
                 day=None,
                 start_time=None,
                 end_time=None,
                 config_id=None):
        """Constructor for the BlackoutWindow1 class"""

        # Initialize members of the class
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
        self.config_id = config_id


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
        start_time = cohesity_management_sdk.models_v2.time_of_day.TimeOfDay.from_dictionary(dictionary.get('startTime')) if dictionary.get('startTime') else None
        end_time = cohesity_management_sdk.models_v2.time_of_day.TimeOfDay.from_dictionary(dictionary.get('endTime')) if dictionary.get('endTime') else None
        config_id = dictionary.get('configId')

        # Return an object of this model
        return cls(day,
                   start_time,
                   end_time,
                   config_id)


