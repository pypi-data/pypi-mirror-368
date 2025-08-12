# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.backup_schedule_and_retention
import cohesity_management_sdk.models_v2.cascaded_target_configuration
import cohesity_management_sdk.models_v2.blackout_window
import cohesity_management_sdk.models_v2.extended_retention_policy
import cohesity_management_sdk.models_v2.targets_configuration
import cohesity_management_sdk.models_v2.retry_options
import cohesity_management_sdk.models_v2.rpo_policy_settings

class ProtectionPolicy(object):

    """Implementation of the 'Protection Policy' model.

    Specifies the details about the Protection Policy.

    Attributes:
        name (string): Specifies the name of the Protection Policy.
        backup_policy (BackupScheduleAndRetention): Specifies the backup
            schedule and retentions of a Protection Policy.
        cascaded_targets_config (list of CascadedTargetConfiguration): Specifies the configuration for cascaded replications. Using
          cascaded replication, replication cluster(Rx) can further replicate and
          archive the snapshot copies to further targets. Its recommended to create
          cascaded configuration where protection group will be created.
        description (string): Specifies the description of the Protection
            Policy.
        blackout_window (list of BlackoutWindow): List of Blackout Windows. If
            specified, this field defines blackout periods when new Group Runs
            are not started. If a Group Run has been scheduled but not yet
            executed and the blackout period starts, the behavior depends on
            the policy field AbortInBlackoutPeriod.
        extended_retention (list of ExtendedRetentionPolicy): Specifies
            additional retention policies that should be applied to the backup
            snapshots. A backup snapshot will be retained up to a time that is
            the maximum of all retention policies that are applicable to it.
        enable_smart_local_retention_adjustment (bool): Specifies whether smart local retention adjustment is enabled
          or not. If enabled, local retention would be extended upon failure of any
          outgoing replications or archivals. Later, if manual intervention causes
          the failed copies to succeed, retention would automatically be reduced.
        remote_target_policy (TargetsConfiguration): Specifies the
            replication, archival and cloud spin targets of Protection
            Policy.
        retry_options (RetryOptions): Retry Options of a Protection Policy
            when a Protection Group run fails.
        data_lock (DataLock1Enum): This field is now deprecated. Please use
            the DataLockConfig in the backup retention.
        is_cbs_enabled (bool): Specifies true if Calender Based Schedule is supported by client.
          Default value is assumed as false for this feature.
        last_modification_time_usecs (long|int): Specifies the last time this Policy was updated. If this is passed
          into a PUT request, then the backend will validate that the timestamp passed
          in matches the time that the policy was actually last modified. If the two
          timestamps do not match, then the request will be rejected with a stale
          error.
        rpo_policy_settings (RPOPolicySettings): Specifies all the additional settings that are applicable only
          to an RPO policy. This can include storage domain, settings of different
          environments, etc.
        skip_interval_mins (long|int): Specifies the period of time before skipping the execution of
          new group Runs if an existing queued group Run of the same Protection group
          has not started. For example if this field is set to 30 minutes and a group
          Run is scheduled to start at 5:00 AM every day but does not start due to
          conflicts (such as too many groups are running). If the new group Run does
          not start by 5:30AM, the Cohesity Cluster will skip the new group Run. If
          the original group Run completes before 5:30AM the next day, a new group
          Run is created and starts executing. This field is optional.
        version (long|int): Specifies the current policy verison. Policy version is incremented
          for optionally supporting new features and differentialting across releases.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "backup_policy":'backupPolicy',
        "cascaded_targets_config":'cascadedTargetsConfig',
        "description":'description',
        "blackout_window":'blackoutWindow',
        "extended_retention":'extendedRetention',
        "enable_smart_local_retention_adjustment":'enableSmartLocalRetentionAdjustment',
        "remote_target_policy":'remoteTargetPolicy',
        "retry_options":'retryOptions',
        "data_lock":'dataLock',
        "is_cbs_enabled":'isCBSEnabled',
        "last_modification_time_usecs":'lastModificationTimeUsecs',
        "rpo_policy_settings":'rpoPolicySettings',
        "skip_interval_mins":'skipIntervalMins',
        "version":'version'
    }

    def __init__(self,
                 name=None,
                 backup_policy=None,
                 cascaded_targets_config=None,
                 description=None,
                 blackout_window=None,
                 extended_retention=None,
                 enable_smart_local_retention_adjustment=None,
                 remote_target_policy=None,
                 retry_options=None,
                 data_lock=None,
                 is_cbs_enabled=None,
                 last_modification_time_usecs=None,
                 rpo_policy_settings=None,
                 skip_interval_mins=None,
                 version=None):
        """Constructor for the ProtectionPolicy class"""

        # Initialize members of the class
        self.name = name
        self.backup_policy = backup_policy
        self.cascaded_targets_config = cascaded_targets_config
        self.description = description
        self.blackout_window = blackout_window
        self.extended_retention = extended_retention
        self.enable_smart_local_retention_adjustment = enable_smart_local_retention_adjustment
        self.remote_target_policy = remote_target_policy
        self.retry_options = retry_options
        self.data_lock = data_lock
        self.is_cbs_enabled = is_cbs_enabled
        self.last_modification_time_usecs = last_modification_time_usecs
        self.rpo_policy_settings = rpo_policy_settings
        self.skip_interval_mins = skip_interval_mins
        self.version = version


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
        name = dictionary.get('name')
        backup_policy = cohesity_management_sdk.models_v2.backup_schedule_and_retention.BackupScheduleAndRetention.from_dictionary(dictionary.get('backupPolicy')) if dictionary.get('backupPolicy') else None
        cascaded_targets_config = None
        if dictionary.get("cascadedTargetsConfig") is not None:
            cascaded_targets_config = list()
            for structure in dictionary.get('cascadedTargetsConfig'):
                cascaded_targets_config.append(cohesity_management_sdk.models_v2.cascaded_target_configuration.CascadedTargetConfiguration.from_dictionary(structure))
        description = dictionary.get('description')
        blackout_window = None
        if dictionary.get("blackoutWindow") is not None:
            blackout_window = list()
            for structure in dictionary.get('blackoutWindow'):
                blackout_window.append(cohesity_management_sdk.models_v2.blackout_window.BlackoutWindow.from_dictionary(structure))
        extended_retention = None
        if dictionary.get("extendedRetention") is not None:
            extended_retention = list()
            for structure in dictionary.get('extendedRetention'):
                extended_retention.append(cohesity_management_sdk.models_v2.extended_retention_policy.ExtendedRetentionPolicy.from_dictionary(structure))
        enable_smart_local_retention_adjustment = dictionary.get('enableSmartLocalRetentionAdjustment')
        remote_target_policy = cohesity_management_sdk.models_v2.targets_configuration.TargetsConfiguration.from_dictionary(dictionary.get('remoteTargetPolicy')) if dictionary.get('remoteTargetPolicy') else None
        retry_options = cohesity_management_sdk.models_v2.retry_options.RetryOptions.from_dictionary(dictionary.get('retryOptions')) if dictionary.get('retryOptions') else None
        data_lock = dictionary.get('dataLock')
        is_cbs_enabled = dictionary.get('isCBSEnabled')
        last_modification_time_usecs = dictionary.get('lastModificationTimeUsecs')
        rpo_policy_settings = cohesity_management_sdk.models_v2.rpo_policy_settings.RPOPolicySettings.from_dictionary(
            dictionary.get('rpoPolicySettings')) if dictionary.get('rpoPolicySettings') else None
        skip_interval_mins = dictionary.get('skipIntervalMins')
        version = dictionary.get('version')

        # Return an object of this model
        return cls(name,
                   backup_policy,
                   cascaded_targets_config,
                   description,
                   blackout_window,
                   extended_retention,
                   enable_smart_local_retention_adjustment,
                   remote_target_policy,
                   retry_options,
                   data_lock,
                   is_cbs_enabled,
                   last_modification_time_usecs,
                   rpo_policy_settings,
                   skip_interval_mins,
                   version)