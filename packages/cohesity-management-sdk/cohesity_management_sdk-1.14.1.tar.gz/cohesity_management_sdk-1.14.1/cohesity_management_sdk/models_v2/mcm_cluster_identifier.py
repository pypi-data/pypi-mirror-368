# -*- coding: utf-8 -*-


class MCMClusterIdentifier(object):

    """Implementation of the 'MCM Cluster Identifier.' model.

    Specifies the MCM cluster identifier.

    Attributes:
        cluster_id (long|int): Specifies the cluster id of the cluster.
        cluster_incarnation_id (long|int): Specifies the incarnation id of the
            cluster.
        region_id (string): Specifies the region id of the cluster. Only valid
            for DMaaS clusters.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cluster_id":'clusterId',
        "cluster_incarnation_id":'clusterIncarnationId',
        "region_id":'regionId'
    }

    def __init__(self,
                 cluster_id=None,
                 cluster_incarnation_id=None,
                 region_id=None):
        """Constructor for the MCMClusterIdentifier class"""

        # Initialize members of the class
        self.cluster_id = cluster_id
        self.cluster_incarnation_id = cluster_incarnation_id
        self.region_id = region_id


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
        region_id = dictionary.get('regionId')

        # Return an object of this model
        return cls(cluster_id,
                   cluster_incarnation_id,
                   region_id)


