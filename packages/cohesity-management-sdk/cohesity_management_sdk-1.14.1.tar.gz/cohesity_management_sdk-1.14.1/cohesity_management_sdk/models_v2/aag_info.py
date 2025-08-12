# -*- coding: utf-8 -*-


class AAGInfo(object):

    """Implementation of the 'AAGInfo' model.

    Object details for Mssql.

    Attributes:
        object_id (long|int): Specifies the AAG object Id.
        name (string): Specifies the AAG name.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_id":'objectId',
        "name":'name'
    }

    def __init__(self,
                 object_id=None,
                 name=None):
        """Constructor for the AAGInfo class"""

        # Initialize members of the class
        self.object_id = object_id
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
        object_id = dictionary.get('objectId')
        name = dictionary.get('name')

        # Return an object of this model
        return cls(object_id,
                   name)


