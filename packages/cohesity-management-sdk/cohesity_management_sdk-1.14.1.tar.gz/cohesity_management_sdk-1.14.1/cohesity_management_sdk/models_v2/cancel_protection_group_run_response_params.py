# -*- coding: utf-8 -*-

class CancelProtectionGroupRunResponseParams(object):

    """Implementation of the 'CancelProtectionGroupRunResponseParams' model.

    Specifies the response of a cancel action on protection runs.

    Attributes:
        run_id (string): Specifies a unique run id of the Protection Group run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "run_id":'runId'
    }

    def __init__(self, run_id):
        """Constructor for the CancelProtectionGroupRunResponseParams class"""

        # Initialize members of the class
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
        run_id = dictionary.get('runId')

        # Return an object of this model
        return cls(run_id)


