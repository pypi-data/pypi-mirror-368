# -*- coding: utf-8 -*-


class NodeSpecificResponse(object):

    """Implementation of the 'Node specific response.' model.

    Specifies node specific response of cluster create.

    Attributes:
        node_id (long|int): Specifies the id of the node.
        node_ip (long|int): Specifies the Ip address of the node.
        message (string): Specifies optional message related to node status.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "node_id":'nodeId',
        "node_ip":'nodeIp',
        "message":'message'
    }

    def __init__(self,
                 node_id=None,
                 node_ip=None,
                 message=None):
        """Constructor for the NodeSpecificResponse class"""

        # Initialize members of the class
        self.node_id = node_id
        self.node_ip = node_ip
        self.message = message


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
        node_id = dictionary.get('nodeId')
        node_ip = dictionary.get('nodeIp')
        message = dictionary.get('message')

        # Return an object of this model
        return cls(node_id,
                   node_ip,
                   message)


