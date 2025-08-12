# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.extended_retention_schedule
import cohesity_management_sdk.models_v2.retention

class ExtendedRetentionPolicy(object):

    """Implementation of the 'Extended Retention Policy.' model.

    Specifies additional retention policies to apply to backup snapshots.

    Attributes:
        schedule (ExtendedRetentionSchedule): Specifies a schedule frequency
            and schedule unit for Extended Retentions.
        retention (Retention): Specifies the retention of a backup.
        run_type (RunType3Enum): The backup run type to which this extended
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
        config_id (string): Specifies the unique identifier for the target
            getting added. This field need to be passed olny when policies are
            updated.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "schedule":'schedule',
        "retention":'retention',
        "run_type":'runType',
        "config_id":'configId'
    }

    def __init__(self,
                 schedule=None,
                 retention=None,
                 run_type=None,
                 config_id=None):
        """Constructor for the ExtendedRetentionPolicy class"""

        # Initialize members of the class
        self.schedule = schedule
        self.retention = retention
        self.run_type = run_type
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
        schedule = cohesity_management_sdk.models_v2.extended_retention_schedule.ExtendedRetentionSchedule.from_dictionary(dictionary.get('schedule')) if dictionary.get('schedule') else None
        retention = cohesity_management_sdk.models_v2.retention.Retention.from_dictionary(dictionary.get('retention')) if dictionary.get('retention') else None
        run_type = dictionary.get('runType')
        config_id = dictionary.get('configId')

        # Return an object of this model
        return cls(schedule,
                   retention,
                   run_type,
                   config_id)


