# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.helios_frequency_schedule

class LogSchedule1(object):

    """Implementation of the 'Log Schedule1' model.

    Specifies settings that defines how frequent log backup will be performed
    for a Protection Group.

    Attributes:
        unit (Unit5Enum): Specifies how often to start new Protection Group
            Runs of a Protection Group. <br>'Minutes' specifies that
            Protection Group run starts periodically after certain number of
            minutes specified in 'frequency' field. <br>'Hours' specifies that
            Protection Group run starts periodically after certain number of
            hours specified in 'frequency' field.
        minute_schedule (HeliosFrequencySchedule): Specifies settings that
            define a schedule for a Protection Group runs to start after
            certain number of minutes.
        hour_schedule (HeliosFrequencySchedule): Specifies settings that
            define a schedule for a Protection Group runs to start after
            certain number of hours.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "unit":'unit',
        "minute_schedule":'minuteSchedule',
        "hour_schedule":'hourSchedule'
    }

    def __init__(self,
                 unit=None,
                 minute_schedule=None,
                 hour_schedule=None):
        """Constructor for the LogSchedule1 class"""

        # Initialize members of the class
        self.unit = unit
        self.minute_schedule = minute_schedule
        self.hour_schedule = hour_schedule


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
        minute_schedule = cohesity_management_sdk.models_v2.helios_frequency_schedule.HeliosFrequencySchedule.from_dictionary(dictionary.get('minuteSchedule')) if dictionary.get('minuteSchedule') else None
        hour_schedule = cohesity_management_sdk.models_v2.helios_frequency_schedule.HeliosFrequencySchedule.from_dictionary(dictionary.get('hourSchedule')) if dictionary.get('hourSchedule') else None

        # Return an object of this model
        return cls(unit,
                   minute_schedule,
                   hour_schedule)


