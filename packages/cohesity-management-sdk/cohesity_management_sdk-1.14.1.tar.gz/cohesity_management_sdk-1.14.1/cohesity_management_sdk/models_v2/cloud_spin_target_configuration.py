# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.schedule
import cohesity_management_sdk.models_v2.retention
import cohesity_management_sdk.models_v2.log_retention
import cohesity_management_sdk.models_v2.cancellation_timeout_params
import cohesity_management_sdk.models_v2.cloud_spin_target

class CloudSpinTargetConfiguration(object):

    """Implementation of the 'CloudSpin Target Configuration.' model.

    Specifies settings for copying Snapshots to Cloud. This also specifies the
    retention policy that should be applied to Snapshots after they have been
    copied to Cloud.

    Attributes:
        backup_run_type (BackupRunType1Enum): Specifies which type of run should be copied, if not set, all
          types of runs will be eligible for copying. If set, this will ensure that
          the first run of given type in the scheduled period will get copied. Currently,
          this can only be set to Full.
        config_id (string): Specifies the unique identifier for the target
            getting added. This field need to be passed only when policies are
            being updated.
        schedule (Schedule): Specifies a schedule frequency and schedule unit
            for copying Snapshots to backup targets.
        retention (Retention): Specifies the retention of a backup.
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
        log_retention (LogRetention): Specifies the retention period of log backup in days, months
          or years to retain copied Snapshots on the external target.
        run_timeouts (list of CancellationTimeoutParams): Specifies the replication/archival timeouts for different type
          of runs(kFull, kRegular etc.).
        target (CloudSpinTarget): Specifies the details about Cloud Spin
            target where backup snapshots may be converted and stored.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "backup_run_type":'backupRunType',
        "config_id":'configId',
        "schedule":'schedule',
        "retention":'retention',
        "copy_on_run_success":'copyOnRunSuccess',
        "log_retention":'logRetention',
        "run_timeouts":'runTimeouts',
        "target":'target'
    }

    def __init__(self,
                 backup_run_type=None,
                 config_id=None,
                 schedule=None,
                 retention=None,
                 copy_on_run_success=None,
                 log_retention=None,
                 run_timeouts=None,
                 target=None):
        """Constructor for the CloudSpinTargetConfiguration class"""

        # Initialize members of the class
        self.backup_run_type = backup_run_type
        self.config_id = config_id
        self.schedule = schedule
        self.retention = retention
        self.copy_on_run_success = copy_on_run_success
        self.log_retention = log_retention
        self.run_timeouts = run_timeouts
        self.target = target


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
        backup_run_type = dictionary.get('backupRunType')
        config_id = dictionary.get('configId')
        schedule = cohesity_management_sdk.models_v2.schedule.Schedule.from_dictionary(dictionary.get('schedule')) if dictionary.get('schedule') else None
        retention = cohesity_management_sdk.models_v2.retention.Retention.from_dictionary(dictionary.get('retention')) if dictionary.get('retention') else None
        copy_on_run_success = dictionary.get('copyOnRunSuccess')
        log_rentention = cohesity_management_sdk.models_v2.log_retention.LogRetention.from_dictionary(dictionary.get('logRetention')) if dictionary.get('logRetention') else None
        run_timeouts = None
        if dictionary.get("runTimeouts") is not None:
            run_timeouts = list()
            for structure in dictionary.get('runTimeouts'):
                run_timeouts.append(cohesity_management_sdk.models_v2.cancellation_timeout_params.CancellationTimeoutParams.from_dictionary(structure))
        target = cohesity_management_sdk.models_v2.cloud_spin_target.CloudSpinTarget.from_dictionary(dictionary.get('target')) if dictionary.get('target') else None

        # Return an object of this model
        return cls(backup_run_type,
                   config_id,
                   schedule,
                   retention,
                   copy_on_run_success,
                   log_rentention,
                   run_timeouts,
                   target)