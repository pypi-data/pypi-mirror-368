# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.device_tree_node

class DeviceTreeNonLeafNode(object):

    """Implementation of the 'DeviceTreeNonLeafNode' model.

    Specifies the parameters of a non leaf node in device tree.

    Attributes:
        mtype (Type9Enum): Specifies the children nodes combine type.
        device_length (long|int): Specifies the length of device.
        device_id (long|int): Specifies the id of device.
        children_nodes (list of DeviceTreeNode): Specifies a list of children
            nodes.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type',
        "device_length":'deviceLength',
        "device_id":'deviceId',
        "children_nodes":'childrenNodes'
    }

    def __init__(self,
                 mtype=None,
                 device_length=None,
                 device_id=None,
                 children_nodes=None):
        """Constructor for the DeviceTreeNonLeafNode class"""

        # Initialize members of the class
        self.mtype = mtype
        self.device_length = device_length
        self.device_id = device_id
        self.children_nodes = children_nodes


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
        mtype = dictionary.get('type')
        device_length = dictionary.get('deviceLength')
        device_id = dictionary.get('deviceId')
        children_nodes = None
        if dictionary.get("childrenNodes") is not None:
            children_nodes = list()
            for structure in dictionary.get('childrenNodes'):
                children_nodes.append(cohesity_management_sdk.models_v2.device_tree_node.DeviceTreeNode.from_dictionary(structure))

        # Return an object of this model
        return cls(mtype,
                   device_length,
                   device_id,
                   children_nodes)


