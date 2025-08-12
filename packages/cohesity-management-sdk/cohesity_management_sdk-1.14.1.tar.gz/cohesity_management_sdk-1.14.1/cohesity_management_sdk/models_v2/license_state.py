# -*- coding: utf-8 -*-


class LicenseState(object):

    """Implementation of the 'LicenseState' model.

    TODO: type description here.

    Attributes:
        failed_attempts (long|int): Specifies no of failed attempts at claiming the license server
        state (StateEnum): Specifies the current state of licensing workflow.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "failed_attempts":'failedAttempts',
        "state":'state'
    }

    def __init__(self,
                 failed_attempts=None,
                 state=None,):
        """Constructor for the LicenseState class"""

        # Initialize members of the class
        self.failed_attempts = failed_attempts
        self.state = state


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
        failed_attempts = dictionary.get('failedAttempts')
        state = dictionary.get('state')

        # Return an object of this model
        return cls(failed_attempts,
                   state)