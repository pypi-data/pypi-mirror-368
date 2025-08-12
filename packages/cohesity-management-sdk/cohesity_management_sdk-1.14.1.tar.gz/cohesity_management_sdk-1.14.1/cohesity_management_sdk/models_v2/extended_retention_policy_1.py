# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.extended_retention_schedule_1
import cohesity_management_sdk.models_v2.helios_retention

class ExtendedRetentionPolicy1(object):

    """Implementation of the 'Extended Retention Policy.1' model.

    Specifies additional retention policies to apply to backup snapshots.

    Attributes:
        schedule (ExtendedRetentionSchedule1): Specifies a schedule frequency
            and schedule unit for Extended Retentions.
        retention (HeliosRetention): Specifies the retention of a backup.
        config_id (string): Specifies the unique identifier for the extedned 
            retention getting added. This field should only be set if policy
            is getting updated.
        run_type (RunTypeEnum): The backup run type to which this extended
            retention applies to. If this is not set, the extended retention
            will be applicable to all non-log backup types. Currently, the
            only value that can be set here is Full. 'Regular' indicates a
            incremental (CBT) backup. Incremental backups utilizing CBT (if
            supported) are captured of the target protection objects. The
            first run of a Regular schedule captures all the blocks. 'Full'
            indicates a full (no CBT) backup. A complete backup (all blocks)
            of the target protection objects are always captured and Change
            Block Tracking (CBT) is not utilized. 'Log' indicates a Database
            Log backup. Capture the database transaction logs to allow rolling
            back to a specific point in time. 'System' indicates a system
            backup. System backups are used to do bare metal recovery of the
            system to a specific point in time.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "schedule":'schedule',
        "retention":'retention',
        "config_id":'configId',
        "run_type":'runType'
    }

    def __init__(self,
                 schedule=None,
                 retention=None,
                 config_id=None,
                 run_type=None):
        """Constructor for the ExtendedRetentionPolicy1 class"""

        # Initialize members of the class
        self.schedule = schedule
        self.retention = retention
        self.config_id = config_id
        self.run_type = run_type


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
        schedule = cohesity_management_sdk.models_v2.extended_retention_schedule_1.ExtendedRetentionSchedule1.from_dictionary(dictionary.get('schedule')) if dictionary.get('schedule') else None
        retention = cohesity_management_sdk.models_v2.helios_retention.HeliosRetention.from_dictionary(dictionary.get('retention')) if dictionary.get('retention') else None
        config_id = dictionary.get('configId')
        run_type = dictionary.get('runType')

        # Return an object of this model
        return cls(schedule,
                   retention,
                   config_id,
                   run_type)


