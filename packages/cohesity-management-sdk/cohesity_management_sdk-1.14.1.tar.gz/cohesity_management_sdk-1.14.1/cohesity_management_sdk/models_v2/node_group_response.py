# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.node_group

class NodeGroupResponse(object):

    """Implementation of the 'Node Group Response' model.

    Specifies the details of Node Groups.

    Attributes:
        node_groups (list of NodeGroup): Specifies the details of a Node
            Group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "node_groups":'nodeGroups'
    }

    def __init__(self,
                 node_groups=None):
        """Constructor for the NodeGroupResponse class"""

        # Initialize members of the class
        self.node_groups = node_groups


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
        node_groups = None
        if dictionary.get("nodeGroups") is not None:
            node_groups = list()
            for structure in dictionary.get('nodeGroups'):
                node_groups.append(cohesity_management_sdk.models_v2.node_group.NodeGroup.from_dictionary(structure))

        # Return an object of this model
        return cls(node_groups)


