# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source_replica_object
import cohesity_management_sdk.models_v2.failover_source_cluster_1

class InitFailoverResponse(object):

    """Implementation of the 'InitFailoverResponse' model.

    Specifies the response after succesfully initiating the failover request.

    Attributes:
        replica_to_source_objects (list of SourceReplicaObject): Specifies the
            list of corrosponding source objects mapped with replica objects
            provided at the time of initiating failover request.
        source_cluster_info (FailoverSourceCluster1): Specifies the details
            about source cluster involved in the failover operation.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "replica_to_source_objects":'replicaToSourceObjects',
        "source_cluster_info":'sourceClusterInfo'
    }

    def __init__(self,
                 replica_to_source_objects=None,
                 source_cluster_info=None):
        """Constructor for the InitFailoverResponse class"""

        # Initialize members of the class
        self.replica_to_source_objects = replica_to_source_objects
        self.source_cluster_info = source_cluster_info


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
        replica_to_source_objects = None
        if dictionary.get("replicaToSourceObjects") is not None:
            replica_to_source_objects = list()
            for structure in dictionary.get('replicaToSourceObjects'):
                replica_to_source_objects.append(cohesity_management_sdk.models_v2.source_replica_object.SourceReplicaObject.from_dictionary(structure))
        source_cluster_info = cohesity_management_sdk.models_v2.failover_source_cluster_1.FailoverSourceCluster1.from_dictionary(dictionary.get('sourceClusterInfo')) if dictionary.get('sourceClusterInfo') else None

        # Return an object of this model
        return cls(replica_to_source_objects,
                   source_cluster_info)


