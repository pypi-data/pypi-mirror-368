# -*- coding: utf-8 -*-


class NodeConfigParams(object):

    """Implementation of the 'NodeConfigParams' model.

    Specifies the configuration of the nodes.

    Attributes:
        id (long|int): Specifies the node ID for this node.
        ip (string): Specifies the IP address for the node.
        ipmi_ip (string): Specifies IPMI IP for the node.
        is_compute_node (bool): Specifies whether to use the node for compute only.    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "ip":'ip',
        "ipmi_ip":'ipmiIp',
        "is_compute_node":'isComputeNode'
    }

    def __init__(self,
                 id=None,
                 ip=None,
                 ipmi_ip=None,
                 is_compute_node=None
                 ):
        """Constructor for the NodeConfigParams class"""

        # Initialize members of the class
        self.id = id
        self.ip = ip
        self.ipmi_ip = ipmi_ip
        self.is_compute_node = is_compute_node


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
        id = dictionary.get('id')
        ip = dictionary.get('ip')
        ipmi_ip = dictionary.get('ipmiIp')
        is_compute_node = dictionary.get('isComputeNode')

        # Return an object of this model
        return cls(id, ip, ipmi_ip, is_compute_node)