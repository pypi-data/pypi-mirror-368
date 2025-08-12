# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.cancel_object_run_params

class CancelObjectRunsParams(object):

    """Implementation of the 'CancelObjectRunsParams' model.

    Request to cancel object runs.

    Attributes:
        object_id (long|int): Specifies object id
        runs_config (list of CancelObjectRunParams): Specifies a list of runs
            to cancel. If no runs are specified, then all the outstanding runs
            will be canceled.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_id":'objectId',
        "runs_config":'runsConfig'
    }

    def __init__(self,
                 object_id=None,
                 runs_config=None):
        """Constructor for the CancelObjectRunsParams class"""

        # Initialize members of the class
        self.object_id = object_id
        self.runs_config = runs_config


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
        object_id = dictionary.get('objectId')
        runs_config = None
        if dictionary.get("runsConfig") is not None:
            runs_config = list()
            for structure in dictionary.get('runsConfig'):
                runs_config.append(cohesity_management_sdk.models_v2.cancel_object_run_params.CancelObjectRunParams.from_dictionary(structure))

        # Return an object of this model
        return cls(object_id,
                   runs_config)


