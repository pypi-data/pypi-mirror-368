# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.node_free_disks

class ClusterFreeDisks(object):

    """Implementation of the 'ClusterFreeDisks' model.

    Sepcifies the free disks of cluster.

    Attributes:
        node_free_disks (list of NodeFreeDisks): Specifies list of free disks
            of cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "node_free_disks":'nodeFreeDisks'
    }

    def __init__(self,
                 node_free_disks=None):
        """Constructor for the ClusterFreeDisks class"""

        # Initialize members of the class
        self.node_free_disks = node_free_disks


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
        node_free_disks = None
        if dictionary.get("nodeFreeDisks") is not None:
            node_free_disks = list()
            for structure in dictionary.get('nodeFreeDisks'):
                node_free_disks.append(cohesity_management_sdk.models_v2.node_free_disks.NodeFreeDisks.from_dictionary(structure))

        # Return an object of this model
        return cls(node_free_disks)


