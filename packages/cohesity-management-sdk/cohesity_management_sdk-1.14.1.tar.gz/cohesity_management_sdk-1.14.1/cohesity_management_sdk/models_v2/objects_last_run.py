# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_last_run

class ObjectsLastRun(object):

    """Implementation of the 'ObjectsLastRun' model.

    Last protection run info of objects.

    Attributes:
        object_last_runs (list of ObjectLastRun): Specifies a list of last
            protection runs of objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_last_runs":'objectLastRuns'
    }

    def __init__(self,
                 object_last_runs=None):
        """Constructor for the ObjectsLastRun class"""

        # Initialize members of the class
        self.object_last_runs = object_last_runs


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
        object_last_runs = None
        if dictionary.get("objectLastRuns") is not None:
            object_last_runs = list()
            for structure in dictionary.get('objectLastRuns'):
                object_last_runs.append(cohesity_management_sdk.models_v2.object_last_run.ObjectLastRun.from_dictionary(structure))

        # Return an object of this model
        return cls(object_last_runs)


