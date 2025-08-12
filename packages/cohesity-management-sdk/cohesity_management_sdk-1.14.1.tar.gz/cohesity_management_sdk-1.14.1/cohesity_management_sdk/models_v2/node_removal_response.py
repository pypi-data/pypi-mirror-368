# -*- coding: utf-8 -*-


class NodeRemovalResponse(object):

    """Implementation of the 'Node Removal Response.' model.

    Specifies details of node removal response.

    Attributes:
        marked_for_removal (bool): If true, Node is marked for removal.
        id (long|int): Specifies id of the node.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "marked_for_removal":'markedForRemoval',
        "id":'id'
    }

    def __init__(self,
                 marked_for_removal=None,
                 id=None):
        """Constructor for the NodeRemovalResponse class"""

        # Initialize members of the class
        self.marked_for_removal = marked_for_removal
        self.id = id


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
        marked_for_removal = dictionary.get('markedForRemoval')
        id = dictionary.get('id')

        # Return an object of this model
        return cls(marked_for_removal,
                   id)


