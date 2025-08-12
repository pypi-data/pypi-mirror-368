# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.cancel_object_runs_result

class CancelObjectRunsResults(object):

    """Implementation of the 'CancelObjectRunsResults' model.

    Results after canceling object runs. If no errors happen, this will not be
    returned.

    Attributes:
        results (list of CancelObjectRunsResult): Specifies results after
            canceling object runs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "results":'results'
    }

    def __init__(self,
                 results=None):
        """Constructor for the CancelObjectRunsResults class"""

        # Initialize members of the class
        self.results = results


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
        results = None
        if dictionary.get("results") is not None:
            results = list()
            for structure in dictionary.get('results'):
                results.append(cohesity_management_sdk.models_v2.cancel_object_runs_result.CancelObjectRunsResult.from_dictionary(structure))

        # Return an object of this model
        return cls(results)


