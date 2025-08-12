# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.backup_schedule_and_retention
import cohesity_management_sdk.models_v2.blackout_window
import cohesity_management_sdk.models_v2.extended_retention_policy
import cohesity_management_sdk.models_v2.targets_configuration
import cohesity_management_sdk.models_v2.retry_options
import cohesity_management_sdk.models_v2.rpo_policy_settings

class ProtectionPolicy2(object):

    """Implementation of the 'Protection Policy2' model.

    Specifies the details about the Protection Policy.

    Attributes:
        name (string): Specifies the name of the Protection Policy.
        backup_policy (BackupScheduleAndRetention): Specifies the backup
            schedule and retentions of a Protection Policy.
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
        remote_target_policy (TargetsConfiguration): Specifies the
            replication, archival and cloud spin targets of Protection
            Policy.
        retry_options (RetryOptions): Retry Options of a Protection Policy
            when a Protection Group run fails.
        data_lock (DataLock1Enum): This field is now deprecated. Please use
            the DataLockConfig in the backup retention.
        id (string): Specifies a unique Policy id assigned by the Cohesity
            Cluster.
        template_id (string): Specifies the parent policy template id to which
            the policy is linked to. This field is set only when policy is
            created from template.
        is_usable (bool): This field is set to true if the linked policy which
            is internally created from a policy templates qualifies as usable
            to create more policies on the cluster. If the linked policy is
            partially filled and can not create a working policy then this
            field will be set to false. In case of normal policy created on
            the cluster, this field wont be populated.
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
        "description":'description',
        "blackout_window":'blackoutWindow',
        "extended_retention":'extendedRetention',
        "remote_target_policy":'remoteTargetPolicy',
        "retry_options":'retryOptions',
        "data_lock":'dataLock',
        "id":'id',
        "template_id":'templateId',
        "is_usable":'isUsable',
        "rpo_policy_settings":'rpoPolicySettings',
        "skip_interval_mins":'skipIntervalMins',
        "version":'version'
    }

    def __init__(self,
                 name=None,
                 backup_policy=None,
                 description=None,
                 blackout_window=None,
                 extended_retention=None,
                 remote_target_policy=None,
                 retry_options=None,
                 data_lock=None,
                 id=None,
                 template_id=None,
                 is_usable=None,
                 rpo_policy_settings=None,
                 skip_interval_mins=None,
                 version=None):
        """Constructor for the ProtectionPolicy2 class"""

        # Initialize members of the class
        self.name = name
        self.backup_policy = backup_policy
        self.description = description
        self.blackout_window = blackout_window
        self.extended_retention = extended_retention
        self.remote_target_policy = remote_target_policy
        self.retry_options = retry_options
        self.data_lock = data_lock
        self.id = id
        self.template_id = template_id
        self.is_usable = is_usable
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
        remote_target_policy = cohesity_management_sdk.models_v2.targets_configuration.TargetsConfiguration.from_dictionary(dictionary.get('remoteTargetPolicy')) if dictionary.get('remoteTargetPolicy') else None
        retry_options = cohesity_management_sdk.models_v2.retry_options.RetryOptions.from_dictionary(dictionary.get('retryOptions')) if dictionary.get('retryOptions') else None
        data_lock = dictionary.get('dataLock')
        id = dictionary.get('id')
        template_id = dictionary.get('templateId')
        is_usable = dictionary.get('isUsable')
        rpo_policy_settings = cohesity_management_sdk.models_v2.rpo_policy_settings.RPOPolicySettings.from_dictionary(
            dictionary.get('rpoPolicySettings')) if dictionary.get('rpoPolicySettings') else None
        skip_interval_mins = dictionary.get('skipIntervalMins')
        version = dictionary.get('version')

        # Return an object of this model
        return cls(name,
                   backup_policy,
                   description,
                   blackout_window,
                   extended_retention,
                   remote_target_policy,
                   retry_options,
                   data_lock,
                   id,
                   template_id,
                   is_usable,
                   rpo_policy_settings,
                   skip_interval_mins,
                   version)