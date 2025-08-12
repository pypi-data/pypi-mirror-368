# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.full_schedule_1
import cohesity_management_sdk.models_v2.retention

class FullScheduleAndRetention(object):

    """Implementation of the 'Full Schedule and Retention' model.

    Specifies the settings to schedule the full backup and retention
      for each schedule.

    Attributes:
        retention (Retention): Specifies the Retention period for full backup schedule mentioned
          above.
        schedule (FullSchedule1): Specifies settings that defines how frequent
            full backup will be performed for a Protection Group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "retention":'retention',
        "schedule":'schedule'
    }

    def __init__(self,
                 retention=None,
                 schedule=None):
        """Constructor for the FullScheduleAndRetention class"""

        # Initialize members of the class
        self.retention = retention
        self.schedule = schedule


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
        retention = cohesity_management_sdk.models_v2.retention.Retention.from_dictionary(dictionary.get('retention')) if dictionary.get('retention') else None
        schedule = cohesity_management_sdk.models_v2.full_schedule_1.FullSchedule1.from_dictionary(dictionary.get('schedule')) if dictionary.get('schedule') else None

        # Return an object of this model
        return cls(retention,schedule)