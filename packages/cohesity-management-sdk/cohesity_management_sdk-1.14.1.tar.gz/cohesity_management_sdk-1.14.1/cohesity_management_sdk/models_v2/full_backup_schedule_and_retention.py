# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.full_schedule

class FullBackupScheduleAndRetention(object):

    """Implementation of the 'Full Backup Schedule and Retention.' model.

    Specifies full backup settings for a Protection Group.

    Attributes:
        schedule (FullSchedule): Specifies settings that defines how frequent
            full backup will be performed for a Protection Group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "schedule":'schedule'
    }

    def __init__(self,
                 schedule=None):
        """Constructor for the FullBackupScheduleAndRetention class"""

        # Initialize members of the class
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
        schedule = cohesity_management_sdk.models_v2.full_schedule.FullSchedule.from_dictionary(dictionary.get('schedule')) if dictionary.get('schedule') else None

        # Return an object of this model
        return cls(schedule)


