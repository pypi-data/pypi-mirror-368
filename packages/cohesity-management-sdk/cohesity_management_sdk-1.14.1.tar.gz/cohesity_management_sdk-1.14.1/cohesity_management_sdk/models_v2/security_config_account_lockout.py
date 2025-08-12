# -*- coding: utf-8 -*-


class SecurityConfigAccountLockout(object):

    """Implementation of the 'SecurityConfigAccountLockout' model.

    Specifies security config for account lockout.

    Attributes:
        max_failed_login_attempts (int): Specifies the maximum number of
            consecutive fail login attempts.
        failed_login_lock_time_duration_mins (int): Specifies the time
            duration within which the consecutive failed login attempts causes
            a local user account to be locked and the lockout duration time
            due to that.
        inactivity_time_days (int): Specifies the lockout inactivity time
            range in days.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "max_failed_login_attempts":'maxFailedLoginAttempts',
        "failed_login_lock_time_duration_mins":'failedLoginLockTimeDurationMins',
        "inactivity_time_days":'inactivityTimeDays'
    }

    def __init__(self,
                 max_failed_login_attempts=None,
                 failed_login_lock_time_duration_mins=None,
                 inactivity_time_days=None):
        """Constructor for the SecurityConfigAccountLockout class"""

        # Initialize members of the class
        self.max_failed_login_attempts = max_failed_login_attempts
        self.failed_login_lock_time_duration_mins = failed_login_lock_time_duration_mins
        self.inactivity_time_days = inactivity_time_days


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
        max_failed_login_attempts = dictionary.get('maxFailedLoginAttempts')
        failed_login_lock_time_duration_mins = dictionary.get('failedLoginLockTimeDurationMins')
        inactivity_time_days = dictionary.get('inactivityTimeDays')

        # Return an object of this model
        return cls(max_failed_login_attempts,
                   failed_login_lock_time_duration_mins,
                   inactivity_time_days)


