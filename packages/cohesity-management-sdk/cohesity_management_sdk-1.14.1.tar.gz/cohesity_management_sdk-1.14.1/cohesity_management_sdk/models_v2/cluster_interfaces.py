# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.node_interfaces

class ClusterInterfaces(object):

    """Implementation of the 'Cluster Interfaces' model.

    Specifies the interfaces present on a Cluster grouped by the Node where
    they are present.

    Attributes:
        nodes (list of NodeInterfaces): Specifies the list of nodes present in
            the cluster. If the request was sent to a free node, then this
            list will have exactly one entry.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "nodes":'nodes'
    }

    def __init__(self,
                 nodes=None):
        """Constructor for the ClusterInterfaces class"""

        # Initialize members of the class
        self.nodes = nodes


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
        nodes = None
        if dictionary.get("nodes") is not None:
            nodes = list()
            for structure in dictionary.get('nodes'):
                nodes.append(cohesity_management_sdk.models_v2.node_interfaces.NodeInterfaces.from_dictionary(structure))

        # Return an object of this model
        return cls(nodes)


