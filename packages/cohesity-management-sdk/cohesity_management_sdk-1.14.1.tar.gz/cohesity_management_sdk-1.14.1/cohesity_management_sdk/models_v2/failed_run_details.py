# -*- coding: utf-8 -*-


class FailedRunDetails(object):

    """Implementation of the 'FailedRunDetails' model.

    Specifies a list of ids of Protection Group Runs that failed to update
    along with error details

    Attributes:
        run_id (string): Specifies the id of the failed run.
        error_message (string): Specifies the error mesage for failed run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "run_id":'runId',
        "error_message":'errorMessage'
    }

    def __init__(self,
                 run_id=None,
                 error_message=None):
        """Constructor for the FailedRunDetails class"""

        # Initialize members of the class
        self.run_id = run_id
        self.error_message = error_message


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
        error_message = dictionary.get('errorMessage')

        # Return an object of this model
        return cls(run_id,
                   error_message)


