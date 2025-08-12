# -*- coding: utf-8 -*-

class PauseProtectionRunActionResponseParams(object):

    """Implementation of the 'PauseProtectionRunActionResponseParams' model.

    Specifies the response of a pause action on protection runs.

    Attributes:
        error (string): Specifies an error occured when perfroming pause of a
            protection run.
        run_id (string): Specifies a unique run id of the Protection Group run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "error": 'error',
        "run_id":'runId'
    }

    def __init__(self, 
                 error=None,
                 run_id=None):
        """Constructor for the PauseProtectionRunActionResponseParams class"""

        # Initialize members of the class
        self.error = error
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
        error = dictionary.get('error')
        run_id = dictionary.get('runId')

        # Return an object of this model
        return cls(error, run_id)


