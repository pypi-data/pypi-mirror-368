# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.network_interface

class NodeInterfaces(object):

    """Implementation of the 'Node Interfaces' model.

    Specifies the interfaces present on a Node.

    Attributes:
        id (long|int): Specifies the id of the node.
        interfaces (list of NetworkInterface): Specifies the list of network
            interfaces present on this Node.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "interfaces":'interfaces'
    }

    def __init__(self,
                 id=None,
                 interfaces=None):
        """Constructor for the NodeInterfaces class"""

        # Initialize members of the class
        self.id = id
        self.interfaces = interfaces


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
        interfaces = None
        if dictionary.get("interfaces") is not None:
            interfaces = list()
            for structure in dictionary.get('interfaces'):
                interfaces.append(cohesity_management_sdk.models_v2.network_interface.NetworkInterface.from_dictionary(structure))

        # Return an object of this model
        return cls(id,
                   interfaces)


