# -*- coding: utf-8 -*-


class NodeResetState(object):

    """Implementation of the 'NodeResetState' model.

    Node reset state information

    Attributes:
        node_id (long|int): Node Id
        node_ip (string): Node Ip.
        state (string): Reset state.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "node_id":'nodeId',
        "node_ip":'nodeIp',
        "state":'state'
    }

    def __init__(self,
                 node_id=None,
                 node_ip=None,
                 state=None):
        """Constructor for the NodeResetState class"""

        # Initialize members of the class
        self.node_id = node_id
        self.node_ip = node_ip
        self.state = state


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
        state = dictionary.get('state')

        # Return an object of this model
        return cls(node_id,
                   node_ip,
                   state)


