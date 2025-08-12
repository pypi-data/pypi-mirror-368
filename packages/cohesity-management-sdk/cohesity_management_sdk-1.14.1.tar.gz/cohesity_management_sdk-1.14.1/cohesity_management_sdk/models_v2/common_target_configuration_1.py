# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.schedule_1
import cohesity_management_sdk.models_v2.helios_retention

class CommonTargetConfiguration1(object):

    """Implementation of the 'Common Target Configuration.1' model.

    Specifies common parameters required while setting up additional
    protection target configuration.

    Attributes:
        schedule (Schedule1): Specifies a schedule frequency and schedule unit
            for copying Snapshots to backup targets.
        retention (HeliosRetention): Specifies the retention of a backup.
        copy_on_run_success (bool): Specifies if Snapshots are copied from the
            first completely successful Protection Group Run or the first
            partially successful Protection Group Run occurring at the start
            of the replication schedule. <br> If true, Snapshots are copied
            from the first Protection Group Run occurring at the start of the
            replication schedule that was completely successful i.e. Snapshots
            for all the Objects in the Protection Group were successfully
            captured. <br> If false, Snapshots are copied from the first
            Protection Group Run occurring at the start of the replication
            schedule, even if first Protection Group Run was not completely
            successful i.e. Snapshots were not captured for all Objects in the
            Protection Group.
        config_id (string): Specifies the unique identifier for the target
            getting added. This field need to be passed only when helios
            policies are updated.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "schedule":'schedule',
        "retention":'retention',
        "copy_on_run_success":'copyOnRunSuccess',
        "config_id":'configId'
    }

    def __init__(self,
                 schedule=None,
                 retention=None,
                 copy_on_run_success=None,
                 config_id=None):
        """Constructor for the CommonTargetConfiguration1 class"""

        # Initialize members of the class
        self.schedule = schedule
        self.retention = retention
        self.copy_on_run_success = copy_on_run_success
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
        schedule = cohesity_management_sdk.models_v2.schedule_1.Schedule1.from_dictionary(dictionary.get('schedule')) if dictionary.get('schedule') else None
        retention = cohesity_management_sdk.models_v2.helios_retention.HeliosRetention.from_dictionary(dictionary.get('retention')) if dictionary.get('retention') else None
        copy_on_run_success = dictionary.get('copyOnRunSuccess')
        config_id = dictionary.get('configId')

        # Return an object of this model
        return cls(schedule,
                   retention,
                   copy_on_run_success,
                   config_id)


