# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.retention
import cohesity_management_sdk.models_v2.storage_snap_mgmt_schedule

class StorageArraySnapshotScheduleAndRetention(object):

    """Implementation of the 'StorageArraySnapshotScheduleAndRetention' model.

    Specifies storage snapshot managment backup settings for a Protection
      Group.

    Attributes:
        retention (Retention): Specifies the source type for Universal
            Data Adapter source.
        schedule (StorageArraySnapshotSchedule): Specifies the schedule settings for storage snapshot managment
          backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "retention":'retention',
        "schedule":'schedule'
    }

    def __init__(self,
                 retention=None,
                 schedule=None
                 ):
        """Constructor for the StorageArraySnapshotScheduleAndRetention class"""

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
        retention = cohesity_management_sdk.models_v2.retention.Retention.from_dictionary(
            dictionary.get('retention')
        )
        schedule = cohesity_management_sdk.models_v2.storage_snap_mgmt_schedule.StorageSnapMgmtSchedule.from_dictionary(dictionary.get('schedule'))


        # Return an object of this model
        return cls(retention,
                   schedule)