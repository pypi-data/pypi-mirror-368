# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.cancel_object_runs_params

class CancelObjectRunsRequest(object):

    """Implementation of the 'CancelObjectRunsRequest' model.

    Request to cancel object runs.

    Attributes:
        object_runs (list of CancelObjectRunsParams): Specifies a list of
            object runs to cancel.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_runs":'objectRuns'
    }

    def __init__(self,
                 object_runs=None):
        """Constructor for the CancelObjectRunsRequest class"""

        # Initialize members of the class
        self.object_runs = object_runs


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
        object_runs = None
        if dictionary.get("objectRuns") is not None:
            object_runs = list()
            for structure in dictionary.get('objectRuns'):
                object_runs.append(cohesity_management_sdk.models_v2.cancel_object_runs_params.CancelObjectRunsParams.from_dictionary(structure))

        # Return an object of this model
        return cls(object_runs)


