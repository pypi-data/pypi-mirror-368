# -*- coding: utf-8 -*-


class ClusterType(object):

    """Implementation of the 'Cluster Type' model.

    Cluster Type

    Attributes:
        cluster_type (ClusterType1Enum): Specifies the cluster types.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cluster_type":'clusterType'
    }

    def __init__(self,
                 cluster_type=None):
        """Constructor for the ClusterType class"""

        # Initialize members of the class
        self.cluster_type = cluster_type


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
        cluster_type = dictionary.get('clusterType')

        # Return an object of this model
        return cls(cluster_type)


