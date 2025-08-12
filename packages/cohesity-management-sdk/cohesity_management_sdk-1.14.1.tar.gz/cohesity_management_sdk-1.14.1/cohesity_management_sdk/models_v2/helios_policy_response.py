# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.backup_schedule_and_retention_1
import cohesity_management_sdk.models_v2.blackout_window_1
import cohesity_management_sdk.models_v2.extended_retention_policy_1
import cohesity_management_sdk.models_v2.helios_targets_configuration
import cohesity_management_sdk.models_v2.helios_retry_options

class HeliosPolicyResponse(object):

    """Implementation of the 'HeliosPolicyResponse' model.

    Specifies the details about the Policy.

    Attributes:
        name (string): Specifies the name of the Protection Policy.
        mtype (Type32Enum): Specifies the type of the Protection Policy to be
            created on Helios.
        backup_policy (BackupScheduleAndRetention1): Specifies the backup
            schedule and retentions of a Protection Policy.
        description (string): Specifies the description of the Protection
            Policy.
        blackout_window (list of BlackoutWindow1): List of Blackout Windows.
            If specified, this field defines blackout periods when new Group
            Runs are not started. If a Group Run has been scheduled but not
            yet executed and the blackout period starts, the behavior depends
            on the policy field AbortInBlackoutPeriod.
        extended_retention (list of ExtendedRetentionPolicy1): Specifies
            additional retention policies that should be applied to the backup
            snapshots. A backup snapshot will be retained up to a time that is
            the maximum of all retention policies that are applicable to it.
        remote_target_policy (HeliosTargetsConfiguration): Specifies the
            replication, archival and cloud spin targets of Protection
            Policy.
        retry_options (HeliosRetryOptions): Retry Options of a Protection
            Policy when a Protection Group run fails.
        data_lock (DataLock2Enum): Specifies WORM retention type for the
            snapshots. When a WORM retention type is specified, the snapshots
            of the Protection Groups using this policy will be kept until the
            maximum of the snapshot retention time. During that time, the
            snapshots cannot be deleted.  'Compliance' implies WORM retention
            is set for compliance reason.  'Administrative' implies WORM
            retention is set for administrative purposes.
        id (string): Specifies a unique policy id assigned by the Helios.
        num_linked_policies (long|int): In case of global policy response,
            specifies the number of policies linked to this global policy on
            the cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "mtype":'type',
        "backup_policy":'backupPolicy',
        "description":'description',
        "blackout_window":'blackoutWindow',
        "extended_retention":'extendedRetention',
        "remote_target_policy":'remoteTargetPolicy',
        "retry_options":'retryOptions',
        "data_lock":'dataLock',
        "id":'id',
        "num_linked_policies":'numLinkedPolicies'
    }

    def __init__(self,
                 name=None,
                 mtype=None,
                 backup_policy=None,
                 description=None,
                 blackout_window=None,
                 extended_retention=None,
                 remote_target_policy=None,
                 retry_options=None,
                 data_lock=None,
                 id=None,
                 num_linked_policies=None):
        """Constructor for the HeliosPolicyResponse class"""

        # Initialize members of the class
        self.name = name
        self.mtype = mtype
        self.backup_policy = backup_policy
        self.description = description
        self.blackout_window = blackout_window
        self.extended_retention = extended_retention
        self.remote_target_policy = remote_target_policy
        self.retry_options = retry_options
        self.data_lock = data_lock
        self.id = id
        self.num_linked_policies = num_linked_policies


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
        mtype = dictionary.get('type')
        backup_policy = cohesity_management_sdk.models_v2.backup_schedule_and_retention_1.BackupScheduleAndRetention1.from_dictionary(dictionary.get('backupPolicy')) if dictionary.get('backupPolicy') else None
        description = dictionary.get('description')
        blackout_window = None
        if dictionary.get("blackoutWindow") is not None:
            blackout_window = list()
            for structure in dictionary.get('blackoutWindow'):
                blackout_window.append(cohesity_management_sdk.models_v2.blackout_window_1.BlackoutWindow1.from_dictionary(structure))
        extended_retention = None
        if dictionary.get("extendedRetention") is not None:
            extended_retention = list()
            for structure in dictionary.get('extendedRetention'):
                extended_retention.append(cohesity_management_sdk.models_v2.extended_retention_policy_1.ExtendedRetentionPolicy1.from_dictionary(structure))
        remote_target_policy = cohesity_management_sdk.models_v2.helios_targets_configuration.HeliosTargetsConfiguration.from_dictionary(dictionary.get('remoteTargetPolicy')) if dictionary.get('remoteTargetPolicy') else None
        retry_options = cohesity_management_sdk.models_v2.helios_retry_options.HeliosRetryOptions.from_dictionary(dictionary.get('retryOptions')) if dictionary.get('retryOptions') else None
        data_lock = dictionary.get('dataLock')
        id = dictionary.get('id')
        num_linked_policies = dictionary.get('numLinkedPolicies')

        # Return an object of this model
        return cls(name,
                   mtype,
                   backup_policy,
                   description,
                   blackout_window,
                   extended_retention,
                   remote_target_policy,
                   retry_options,
                   data_lock,
                   id,
                   num_linked_policies)


