# -*- coding: utf-8 -*-


class PauseMetadata(object):

    """Implementation of the 'PauseMetadata' model.

    Encapsulation of all pause related data.

    Attributes:
        last_pause_modification_time_usecs (long|int): Time in usec when the job was
             last paused or unpaused.
        last_paused_by_username (string): The user who last paused this protection group.
        paused_note (string): A note from the user explaining the reason for pausing future
          runs, if applicable.
        user_initiated_pause_requested_time_usecs (long|int): Time in usec when user initiates protection run pause. This field
          gets populated on user initiated pause and gets cleared on user initiated
          resume.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "last_pause_modification_time_usecs":'lastPauseModificationTimeUsecs',
        "last_paused_by_username":'lastPausedByUsername',
        "paused_note":'pausedNote',
        "user_initiated_pause_requested_time_usecs":'userInitiatedPauseRequestedTimeUsecs'
    }

    def __init__(self,
                 last_pause_modification_time_usecs=None,
                 last_paused_by_username=None,
                 paused_note=None,
                 user_initiated_pause_requested_time_usecs=None
                 ):
        """Constructor for the PauseMetadata class"""

        # Initialize members of the class
        self.last_pause_modification_time_usecs = last_pause_modification_time_usecs
        self.last_paused_by_username = last_paused_by_username
        self.paused_note = paused_note
        self.user_initiated_pause_requested_time_usecs = user_initiated_pause_requested_time_usecs

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
        last_pause_modification_time_usecs = dictionary.get('lastPauseModificationTimeUsecs')
        last_paused_by_username = dictionary.get('lastPausedByUsername')
        paused_note = dictionary.get('pausedNote')
        user_initiated_pause_requested_time_usecs = dictionary.get('userInitiatedPauseRequestedTimeUsecs')

        # Return an object of this model
        return cls(last_pause_modification_time_usecs,
                   last_paused_by_username,
                   paused_note,
                   user_initiated_pause_requested_time_usecs)