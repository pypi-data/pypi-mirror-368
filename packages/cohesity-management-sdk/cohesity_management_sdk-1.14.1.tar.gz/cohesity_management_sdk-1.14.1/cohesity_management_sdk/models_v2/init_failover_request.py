# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.failover_source_cluster_1
import cohesity_management_sdk.models_v2.failover_source_cluster

class InitFailoverRequest(object):

    """Implementation of the 'Init Failover Request.' model.

    Specifies the failover request parameters to initiate a failover.

    Attributes:
        source_cluster (FailoverSourceCluster1): Specifies the details about
            source cluster involved in the failover operation.
        replication_cluster (FailoverSourceCluster): Specifies the details
            about replication cluster involved in the failover operation.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_cluster":'sourceCluster',
        "replication_cluster":'replicationCluster'
    }

    def __init__(self,
                 source_cluster=None,
                 replication_cluster=None):
        """Constructor for the InitFailoverRequest class"""

        # Initialize members of the class
        self.source_cluster = source_cluster
        self.replication_cluster = replication_cluster


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
        source_cluster = cohesity_management_sdk.models_v2.failover_source_cluster_1.FailoverSourceCluster1.from_dictionary(dictionary.get('sourceCluster')) if dictionary.get('sourceCluster') else None
        replication_cluster = cohesity_management_sdk.models_v2.failover_source_cluster.FailoverSourceCluster.from_dictionary(dictionary.get('replicationCluster')) if dictionary.get('replicationCluster') else None

        # Return an object of this model
        return cls(source_cluster,
                   replication_cluster)


