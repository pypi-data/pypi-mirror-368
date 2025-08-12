# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.leaf_node_params
import cohesity_management_sdk.models_v2.non_leaf_node_params

class DeviceTreeNode(object):

    """Implementation of the 'DeviceTreeNode' model.

    Specifies the tree structure of a logical volume. The leaves are slices of
    partitions and the other nodes are assemled by combining nodes in some
    mode.

    Attributes:
        is_leaf (bool): Specifies if the node is a leaf node.
        leaf_node_params (LeafNodeParams): Specifies the parameters for a leaf
            node.
        non_leaf_node_params (NonLeafNodeParams): Specifies the parameters for
            a non leaf node.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "is_leaf":'isLeaf',
        "leaf_node_params":'leafNodeParams',
        "non_leaf_node_params":'nonLeafNodeParams'
    }

    def __init__(self,
                 is_leaf=None,
                 leaf_node_params=None,
                 non_leaf_node_params=None):
        """Constructor for the DeviceTreeNode class"""

        # Initialize members of the class
        self.is_leaf = is_leaf
        self.leaf_node_params = leaf_node_params
        self.non_leaf_node_params = non_leaf_node_params


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
        is_leaf = dictionary.get('isLeaf')
        leaf_node_params = cohesity_management_sdk.models_v2.leaf_node_params.LeafNodeParams.from_dictionary(dictionary.get('leafNodeParams')) if dictionary.get('leafNodeParams') else None
        non_leaf_node_params = cohesity_management_sdk.models_v2.non_leaf_node_params.NonLeafNodeParams.from_dictionary(dictionary.get('nonLeafNodeParams')) if dictionary.get('nonLeafNodeParams') else None

        # Return an object of this model
        return cls(is_leaf,
                   leaf_node_params,
                   non_leaf_node_params)


