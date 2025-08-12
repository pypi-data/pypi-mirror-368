# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.alert_target

class ProtectionGroupAlertingPolicy(object):

    """Implementation of the 'ProtectionGroupAlertingPolicy' model.

    Specifies a policy for alerting users of the status of a Protection
    Group.

    Attributes:
        backup_run_status (list of BackupRunStatusEnum): Specifies when to send out alerts. The possible values are kSuccess
          , kFailure, kSlaViolation and kWarning
        alert_targets (list of AlertTarget): Specifies a list of targets to
            receive the alerts.
        raise_object_level_failure_alert (bool): Specifies whether object level alerts are raised for backup failures
          after the backup run.
        raise_object_level_failure_alert_after_last_attempt (bool): Specifies whether object level alerts are raised for backup failures
          after last backup attempt.
        raise_object_level_failure_alert_after_each_attempt (bool): Specifies whether object level alerts are raised for backup failures
          after each backup attempt.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "backup_run_status":'backupRunStatus',
        "alert_targets":'alertTargets',
        "raise_object_level_failure_alert":'raiseObjectLevelFailureAlert',
        "raise_object_level_failure_alert_after_last_attempt":'raiseObjectLevelFailureAlertAfterLastAttempt',
        "raise_object_level_failure_alert_after_each_attempt":'raiseObjectLevelFailureAlertAfterEachAttempt'
    }

    def __init__(self,
                 backup_run_status=None,
                 alert_targets=None,
                 raise_object_level_failure_alert=None,
                 raise_object_level_failure_alert_after_last_attempt=None,
                 raise_object_level_failure_alert_after_each_attempt=None):
        """Constructor for the ProtectionGroupAlertingPolicy class"""

        # Initialize members of the class
        self.backup_run_status = backup_run_status
        self.alert_targets = alert_targets
        self.raise_object_level_failure_alert = raise_object_level_failure_alert
        self.raise_object_level_failure_alert_after_last_attempt = raise_object_level_failure_alert_after_last_attempt
        self.raise_object_level_failure_alert_after_each_attempt = raise_object_level_failure_alert_after_each_attempt


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
        backup_run_status = dictionary.get('backupRunStatus')
        alert_targets = None
        if dictionary.get("alertTargets") is not None:
            alert_targets = list()
            for structure in dictionary.get('alertTargets'):
                alert_targets.append(cohesity_management_sdk.models_v2.alert_target.AlertTarget.from_dictionary(structure))
        raise_object_level_failure_alert = dictionary.get('raiseObjectLevelFailureAlert')
        raise_object_level_failure_alert_after_last_attempt = dictionary.get('raiseObjectLevelFailureAlertAfterLastAttempt')
        raise_object_level_failure_alert_after_each_attempt = dictionary.get('raiseObjectLevelFailureAlertAfterEachAttempt')

        # Return an object of this model
        return cls(backup_run_status,
                   alert_targets,
                   raise_object_level_failure_alert,
                   raise_object_level_failure_alert_after_last_attempt,
                   raise_object_level_failure_alert_after_each_attempt)