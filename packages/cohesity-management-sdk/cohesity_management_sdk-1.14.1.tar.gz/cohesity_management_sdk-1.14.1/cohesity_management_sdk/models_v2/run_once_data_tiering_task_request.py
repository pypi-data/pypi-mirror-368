# -*- coding: utf-8 -*-


class RunOnceDataTieringTaskRequest(object):

    """Implementation of the 'Run once data tiering task request.' model.

    Specifies the request to run tiering task once.

    Attributes:
        uptier_path (string): Ignore the uptiering policy and uptier the
            directory pointed by the 'uptierPath'. If path is '/', then uptier
            everything.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "uptier_path":'uptierPath'
    }

    def __init__(self,
                 uptier_path=None):
        """Constructor for the RunOnceDataTieringTaskRequest class"""

        # Initialize members of the class
        self.uptier_path = uptier_path


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
        uptier_path = dictionary.get('uptierPath')

        # Return an object of this model
        return cls(uptier_path)


