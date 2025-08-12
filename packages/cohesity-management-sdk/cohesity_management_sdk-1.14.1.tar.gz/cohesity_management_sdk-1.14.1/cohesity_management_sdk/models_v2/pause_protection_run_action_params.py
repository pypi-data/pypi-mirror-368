# -*- coding: utf-8 -*-

class PauseProtectionRunActionParams(object):

    """Implementation of the 'PauseProtectionRunActionParams' model.

    Specifies the request to pause a protection run.

    Attributes:
        paused_note (string): A note from the current user explaining the reason for pausing
          runs, if applicable.
        run_id (string): Specifies a unique run id of the Protection Group run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "paused_note":'pausedNote',
        "run_id":'runId'
    }

    def __init__(self,
                 paused_note,
                 run_id):
        """Constructor for the PauseProtectionRunActionParams class"""

        # Initialize members of the class
        self.paused_note = paused_note
        self.run_id = run_id


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
        paused_note = dictionary.get('pausedNote')
        run_id = dictionary.get('runId')

        # Return an object of this model
        return cls(paused_note, run_id)