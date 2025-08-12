# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.email_delivery_target

class AlertingConfig(object):

    """Implementation of the 'AlertingConfig' model.

    Specifies optional settings for alerting.

    Attributes:
        email_addresses (list of string): Exists to maintain backwards
            compatibility with versions before eff8198.
        email_delivery_targets (list of EmailDeliveryTarget): Specifies
            additional email addresses where alert notifications (configured
            in the AlertingPolicy) must be sent.
        raise_object_level_failure_alert (bool): Specifies the boolean to
            raise per object alert for failures.
        raise_object_level_failure_alert_after_each_attempt (bool): Raise per
            object alert for failures after each backup attempt.
        raise_object_level_failure_alert_after_last_attempt (bool): Raise per
            object alert for failures after last backup attempt.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "email_addresses":'emailAddresses',
        "email_delivery_targets":'emailDeliveryTargets',
        "raise_object_level_failure_alert":'raiseObjectLevelFailureAlert',
        "raise_object_level_failure_alert_after_each_attempt":'raiseObjectLevelFailureAlertAfterEachAttempt',
        "raise_object_level_failure_alert_after_last_attempt":'raiseObjectLevelFailureAlertAfterLastAttempt'
    }

    def __init__(self,
                 email_addresses=None,
                 email_delivery_targets=None,
                 raise_object_level_failure_alert=None,
                 raise_object_level_failure_alert_after_each_attempt=None,
                 raise_object_level_failure_alert_after_last_attempt=None):
        """Constructor for the AlertingConfig class"""

        # Initialize members of the class
        self.email_addresses = email_addresses
        self.email_delivery_targets = email_delivery_targets
        self.raise_object_level_failure_alert = raise_object_level_failure_alert
        self.raise_object_level_failure_alert_after_each_attempt = raise_object_level_failure_alert_after_each_attempt
        self.raise_object_level_failure_alert_after_last_attempt = raise_object_level_failure_alert_after_last_attempt


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
        email_delivery_targets = None
        email_addresses = dictionary.get('emailAddresses')
        if dictionary.get("emailDeliveryTargets") is not None:
            email_delivery_targets = list()
            for structure in dictionary.get('emailDeliveryTargets'):
                email_delivery_targets.append(cohesity_management_sdk.models.email_delivery_target.EmailDeliveryTarget.from_dictionary(structure))
        raise_object_level_failure_alert = dictionary.get('raiseObjectLevelFailureAlert')
        raise_object_level_failure_alert_after_each_attempt = dictionary.get('raiseObjectLevelFailureAlertAfterEachAttempt')
        raise_object_level_failure_alert_after_last_attempt = dictionary.get('raiseObjectLevelFailureAlertAfterLastAttempt')

        # Return an object of this model
        return cls(email_addresses,
                   email_delivery_targets,
                   raise_object_level_failure_alert,
                   raise_object_level_failure_alert_after_each_attempt,
                   raise_object_level_failure_alert_after_last_attempt)


