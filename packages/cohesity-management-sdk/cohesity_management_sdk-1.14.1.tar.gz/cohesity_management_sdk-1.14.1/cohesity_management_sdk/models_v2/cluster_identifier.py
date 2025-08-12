# -*- coding: utf-8 -*-


class ClusterIdentifier(object):

    """Implementation of the 'Cluster Identifier' model.

    Specifies the information about a cluster.

    Attributes:
        cluster_id (long|int): Specifies the id of the cluster.
        cluster_incarnation_id (long|int): Specifies the incarnation id of the
            cluster.
        cluster_name (string): Specifies the name of the cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cluster_id":'clusterId',
        "cluster_incarnation_id":'clusterIncarnationId',
        "cluster_name":'clusterName'
    }

    def __init__(self,
                 cluster_id=None,
                 cluster_incarnation_id=None,
                 cluster_name=None):
        """Constructor for the ClusterIdentifier class"""

        # Initialize members of the class
        self.cluster_id = cluster_id
        self.cluster_incarnation_id = cluster_incarnation_id
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
        cluster_incarnation_id = dictionary.get('clusterIncarnationId')
        cluster_name = dictionary.get('clusterName')

        # Return an object of this model
        return cls(cluster_id,
                   cluster_incarnation_id,
                   cluster_name)


