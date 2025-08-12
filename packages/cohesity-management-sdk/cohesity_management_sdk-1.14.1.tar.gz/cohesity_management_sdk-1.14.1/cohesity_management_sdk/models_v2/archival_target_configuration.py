# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.schedule
import cohesity_management_sdk.models_v2.cancellation_timeout_params
import cohesity_management_sdk.models_v2.retention
import cohesity_management_sdk.models_v2.log_retention
import cohesity_management_sdk.models_v2.extended_retention_policy
import cohesity_management_sdk.models_v2.tier_level_settings

class ArchivalTargetConfiguration(object):

    """Implementation of the 'Archival Target Configuration' model.

    Specifies settings for copying Snapshots External Targets (such as AWS or
    Tape). This also specifies the retention policy that should be applied to
    Snapshots after they have been copied to the specified target.

    Attributes:
        backup_run_type (BackupRunType1Enum): Specifies which type of run should be copied, if not set, all
          types of runs will be eligible for copying. If set, this will ensure that
          the first run of given type in the scheduled period will get copied. Currently,
          this can only be set to Full.
        extended_retention (list of ExtendedRetentionPolicy): Specifies additional retention policies that should be applied
            to the archived backup. Archived backup snapshot will be retained up to
            a time that is the maximum of all retention policies that are applicable
            to it.
        schedule (Schedule): Specifies a schedule frequency and schedule unit
            for copying Snapshots to backup targets.
        on_legal_hold (bool): Specifies if the Run is on legal hold.
        retention (Retention): Specifies the retention of a backup.
        run_timeouts (list of CancellationTimeoutParams): Specifies the replication/archival timeouts for different type
          of runs(kFull, kRegular etc.).
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
        config_id (string): Specifies the unique identifier for the target
            getting added. This field need to be passed only when policies are
            being updated.
        target_id (long|int): Specifies the Archival target to copy the
            Snapshots to.
        target_name (string): Specifies the Archival target name where
            Snapshots are copied.
        target_type (TargetTypeEnum): Specifies the Archival target type where
            Snapshots are copied.
        tier_settings (TierLevelSettings): Specifies the tier settings that will be applied to given target.
            If provided target is of type 'cloud', then only tiering can be applied.
            The respective cloud platform details need to be provided here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "backup_run_type": 'backupRunType',
        "extended_retention":'extendedRetention',
        "schedule":'schedule',
        "on_legal_hold":'onLegalHold',
        "retention":'retention',
        "run_timeouts":'runTimeouts',
        "copy_on_run_success":'copyOnRunSuccess',
        "log_retention":'logRetention',
        "config_id":'configId',
        "target_id" : 'targetId' ,
        "target_name":'targetName',
        "target_type":'targetType',
        "tier_settings":'tierSettings'
    }

    def __init__(self,
                 backup_run_type = None,
                 extended_retention=None,
                 schedule=None,
                 on_legal_hold=None,
                 retention=None,
                 run_timeouts=None,
                 copy_on_run_success=None,
                 log_retention=None,
                 config_id=None,
                 target_id=None ,
                 target_name=None,
                 target_type=None,
                 tier_settings=None):
        """Constructor for the ArchivalTargetConfiguration class"""

        # Initialize members of the class
        self.backup_run_type = backup_run_type
        self.extended_retention = extended_retention
        self.schedule = schedule
        self.on_legal_hold = on_legal_hold
        self.retention = retention
        self.run_timeouts = run_timeouts
        self.copy_on_run_success = copy_on_run_success
        self.log_retention = log_retention
        self.config_id = config_id
        self.target_id = target_id
        self.target_name = target_name
        self.target_type = target_type
        self.tier_settings = tier_settings


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
        extended_retention = None
        if dictionary.get("extendedRetention") is not None:
            extended_retention = list()
            for structure in dictionary.get('extendedRetention'):
                extended_retention.append(cohesity_management_sdk.models_v2.extended_retention_policy.ExtendedRetentionPolicy.from_dictionary(structure))
        schedule = cohesity_management_sdk.models_v2.schedule.Schedule.from_dictionary(dictionary.get('schedule')) if dictionary.get('schedule') else None
        on_legal_hold = dictionary.get('onLegalHold')
        retention = cohesity_management_sdk.models_v2.retention.Retention.from_dictionary(dictionary.get('retention')) if dictionary.get('retention') else None
        run_timeouts = None
        if dictionary.get("runTimeouts") is not None:
            run_timeouts = list()
            for structure in dictionary.get('runTimeouts'):
                run_timeouts.append(cohesity_management_sdk.models_v2.cancellation_timeout_params.CancellationTimeoutParams.from_dictionary(structure))
        copy_on_run_success = dictionary.get('copyOnRunSuccess')
        log_retention = cohesity_management_sdk.models_v2.log_retention.LogRetention.from_dictionary(dictionary.get('logRetention')) if dictionary.get('logRetention') else None
        config_id = dictionary.get('configId')
        target_id = dictionary.get('targetId')
        target_name = dictionary.get('targetName')
        target_type = dictionary.get('targetType')
        tier_settings = cohesity_management_sdk.models_v2.tier_level_settings.TierLevelSettings.from_dictionary(dictionary.get('tierSettings')) if dictionary.get('tierSettings') else None

        # Return an object of this model
        return cls(backup_run_type,
                   extended_retention,
                   schedule,
                   on_legal_hold,
                   retention,
                   run_timeouts,
                   copy_on_run_success,
                   log_retention,
                   config_id,
                   target_id ,
                   target_name,
                   target_type,
                   tier_settings)