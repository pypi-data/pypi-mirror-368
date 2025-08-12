# -*- coding: utf-8 -*-


class ProgressTaskStatus(object):

    """Implementation of the 'ProgressTaskStatus' model.

    Progress Task Status

    Attributes:
        progressask_status (ProgressaskStatusEnum): Specifies the progress
            task status.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "progressask_status":'progressaskStatus'
    }

    def __init__(self,
                 progressask_status=None):
        """Constructor for the ProgressTaskStatus class"""

        # Initialize members of the class
        self.progressask_status = progressask_status


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
        progressask_status = dictionary.get('progressaskStatus')

        # Return an object of this model
        return cls(progressask_status)


