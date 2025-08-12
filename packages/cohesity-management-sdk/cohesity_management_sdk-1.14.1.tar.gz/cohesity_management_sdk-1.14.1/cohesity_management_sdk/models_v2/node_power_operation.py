# -*- coding: utf-8 -*-


class NodePowerOperation(object):

    """Implementation of the 'NodePowerOperation' model.

    TODO: type model description here.

    Attributes:
        operation (OperationEnum): The operation clould be poweroff, reboot.
        node_id (long|int): Id of the node to do the specified operation.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "operation":'operation',
        "node_id":'nodeId'
    }

    def __init__(self,
                 operation=None,
                 node_id=None):
        """Constructor for the NodePowerOperation class"""

        # Initialize members of the class
        self.operation = operation
        self.node_id = node_id


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
        operation = dictionary.get('operation')
        node_id = dictionary.get('nodeId')

        # Return an object of this model
        return cls(operation,
                   node_id)


