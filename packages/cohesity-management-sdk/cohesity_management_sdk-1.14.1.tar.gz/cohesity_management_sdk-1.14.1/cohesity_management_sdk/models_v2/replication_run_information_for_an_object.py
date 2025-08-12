# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.replication_result_for_a_target

class ReplicationRunInformationForAnObject(object):

    """Implementation of the 'Replication run information for an object.' model.

    Specifies information about replication run for an object.

    Attributes:
        replication_target_results (list of ReplicationResultForATarget):
            Replication result for a target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "replication_target_results":'replicationTargetResults'
    }

    def __init__(self,
                 replication_target_results=None):
        """Constructor for the ReplicationRunInformationForAnObject class"""

        # Initialize members of the class
        self.replication_target_results = replication_target_results


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
        replication_target_results = None
        if dictionary.get("replicationTargetResults") is not None:
            replication_target_results = list()
            for structure in dictionary.get('replicationTargetResults'):
                replication_target_results.append(cohesity_management_sdk.models_v2.replication_result_for_a_target.ReplicationResultForATarget.from_dictionary(structure))

        # Return an object of this model
        return cls(replication_target_results)


