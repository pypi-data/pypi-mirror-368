# -*- coding: utf-8 -*-


class Volume1(object):

    """Implementation of the 'Volume1' model.

    Specifies the id and name of the parent volume to recover to. This volume
    will be the target of the recovery.

    Attributes:
        id (long|int): Specifies the id of the object.
        name (string): Specifies the name of the object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name'
    }

    def __init__(self,
                 id=None,
                 name=None):
        """Constructor for the Volume1 class"""

        # Initialize members of the class
        self.id = id
        self.name = name


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
        name = dictionary.get('name')

        # Return an object of this model
        return cls(id,
                   name)


