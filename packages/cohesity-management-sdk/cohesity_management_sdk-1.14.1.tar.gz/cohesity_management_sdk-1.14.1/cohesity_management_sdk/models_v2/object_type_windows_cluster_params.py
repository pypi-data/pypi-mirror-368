# -*- coding: utf-8 -*-

class ObjectTypeWindowsClusterParams(object):

    """Implementation of the 'ObjectTypeWindowsClusterParams' model.


    Attributes:
        cluster_source_type (string): Specifies the type of cluster resource this source represents.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cluster_source_type" :'clusterSourceType'
    }

    def __init__(self,
                 cluster_source_type=None):
        """Constructor for the ObjectTypeWindowsClusterParams class"""

        # Initialize members of the class
        self.cluster_source_type = cluster_source_type


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
        cluster_source_type = dictionary.get('clusterSourceType')

        # Return an object of this model
        return cls(cluster_source_type)