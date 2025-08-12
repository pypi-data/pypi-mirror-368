# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_protection_group_run_response_parameters

class ObjectRuns(object):

    """Implementation of the 'ObjectRuns' model.

    Protection runs of an object.

    Attributes:
        runs (list of CommonProtectionGroupRunResponseParameters): Specifies
            the list of protection runs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "runs":'runs'
    }

    def __init__(self,
                 runs=None):
        """Constructor for the ObjectRuns class"""

        # Initialize members of the class
        self.runs = runs


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
        runs = None
        if dictionary.get("runs") is not None:
            runs = list()
            for structure in dictionary.get('runs'):
                runs.append(cohesity_management_sdk.models_v2.common_protection_group_run_response_parameters.CommonProtectionGroupRunResponseParameters.from_dictionary(structure))

        # Return an object of this model
        return cls(runs)


