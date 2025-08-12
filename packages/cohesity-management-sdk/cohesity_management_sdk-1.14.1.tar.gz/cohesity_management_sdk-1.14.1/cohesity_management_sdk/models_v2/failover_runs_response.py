# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.planned_run_poll_status

class FailoverRunsResponse(object):

    """Implementation of the 'FailoverRunsResponse' model.

    Specifies the response upon creating a special run during failover
    workflow.

    Attributes:
        failover_planned_runs (list of PlannedRunPollStatus): Specifies the
            list of planned runs created during various planeed failover
            workflows. Each planned run is uniqely identified by falioverId
            and runId.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "failover_planned_runs":'failoverPlannedRuns'
    }

    def __init__(self,
                 failover_planned_runs=None):
        """Constructor for the FailoverRunsResponse class"""

        # Initialize members of the class
        self.failover_planned_runs = failover_planned_runs


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
        failover_planned_runs = None
        if dictionary.get("failoverPlannedRuns") is not None:
            failover_planned_runs = list()
            for structure in dictionary.get('failoverPlannedRuns'):
                failover_planned_runs.append(cohesity_management_sdk.models_v2.planned_run_poll_status.PlannedRunPollStatus.from_dictionary(structure))

        # Return an object of this model
        return cls(failover_planned_runs)


