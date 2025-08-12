# -*- coding: utf-8 -*-


class SecurityConfigSessionConfiguration(object):

    """Implementation of the 'SecurityConfigSessionConfiguration' model.

    Specifies configuration for user sessions.

    Attributes:
        absolute_timeout (long|int): Specifies absolute session expiration
            time in seconds.
        inactivity_timeout (long|int): Specifies inactivity session expiration
            time in seconds.
        limit_sessions (bool): Specifies if limitations on number of active
            sessions is enabled or not.
        session_limit_per_user (long|int): Specifies maximum number of active
            sessions allowed per user. This applies only when limitSessions is
            enabled.
        session_limit_system_wide (long|int): Specifies maximum number of
            active sessions allowed system wide. This applies only when
            limitSessions is enabled.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "absolute_timeout":'absoluteTimeout',
        "inactivity_timeout":'inactivityTimeout',
        "limit_sessions":'limitSessions',
        "session_limit_per_user":'sessionLimitPerUser',
        "session_limit_system_wide":'sessionLimitSystemWide'
    }

    def __init__(self,
                 absolute_timeout=None,
                 inactivity_timeout=None,
                 limit_sessions=None,
                 session_limit_per_user=None,
                 session_limit_system_wide=None):
        """Constructor for the SecurityConfigSessionConfiguration class"""

        # Initialize members of the class
        self.absolute_timeout = absolute_timeout
        self.inactivity_timeout = inactivity_timeout
        self.limit_sessions = limit_sessions
        self.session_limit_per_user = session_limit_per_user
        self.session_limit_system_wide = session_limit_system_wide


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
        absolute_timeout = dictionary.get('absoluteTimeout')
        inactivity_timeout = dictionary.get('inactivityTimeout')
        limit_sessions = dictionary.get('limitSessions')
        session_limit_per_user = dictionary.get('sessionLimitPerUser')
        session_limit_system_wide = dictionary.get('sessionLimitSystemWide')

        # Return an object of this model
        return cls(absolute_timeout,
                   inactivity_timeout,
                   limit_sessions,
                   session_limit_per_user,
                   session_limit_system_wide)


