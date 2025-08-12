# -*- coding: utf-8 -*-


class ClusterTargetConfiguration(object):

    """Implementation of the 'Cluster Target Configuration' model.

    Specifies the configuration for adding remote cluster as repilcation
    target

    Attributes:
        cluster_id (long|int): Specifies the cluster id of the target
            replication cluster.
        cluster_name (string): Specifies the cluster name of the target
            replication cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cluster_id":'clusterId',
        "cluster_name":'clusterName'
    }

    def __init__(self,
                 cluster_id=None,
                 cluster_name=None):
        """Constructor for the ClusterTargetConfiguration class"""

        # Initialize members of the class
        self.cluster_id = cluster_id
        self.cluster_name = cluster_name


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
        cluster_id = dictionary.get('clusterId')
        cluster_name = dictionary.get('clusterName')

        # Return an object of this model
        return cls(cluster_id,
                   cluster_name)


