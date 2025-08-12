# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.planned_failover_params_2
import cohesity_management_sdk.models_v2.unplanned_failover_params_2

class CreateViewFailoverRequest(object):

    """Implementation of the 'CreateViewFailoverRequest' model.

    Specifies the request parameters to create a view failover task.

    Attributes:
        mtype (Type20Enum): Specifies the failover type.<br> 'Planned'
            indicates this is a planned failover.<br> 'Unplanned' indicates
            this is an unplanned failover, which is used when source cluster
            is down.
        planned_failover_params (PlannedFailoverParams2): Specifies parameters
            to create a planned failover.
        unplanned_failover_params (UnplannedFailoverParams2): Specifies
            parameters to create an unplanned failover.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type',
        "planned_failover_params":'plannedFailoverParams',
        "unplanned_failover_params":'unplannedFailoverParams'
    }

    def __init__(self,
                 mtype=None,
                 planned_failover_params=None,
                 unplanned_failover_params=None):
        """Constructor for the CreateViewFailoverRequest class"""

        # Initialize members of the class
        self.mtype = mtype
        self.planned_failover_params = planned_failover_params
        self.unplanned_failover_params = unplanned_failover_params


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
        mtype = dictionary.get('type')
        planned_failover_params = cohesity_management_sdk.models_v2.planned_failover_params_2.PlannedFailoverParams2.from_dictionary(dictionary.get('plannedFailoverParams')) if dictionary.get('plannedFailoverParams') else None
        unplanned_failover_params = cohesity_management_sdk.models_v2.unplanned_failover_params_2.UnplannedFailoverParams2.from_dictionary(dictionary.get('unplannedFailoverParams')) if dictionary.get('unplannedFailoverParams') else None

        # Return an object of this model
        return cls(mtype,
                   planned_failover_params,
                   unplanned_failover_params)


