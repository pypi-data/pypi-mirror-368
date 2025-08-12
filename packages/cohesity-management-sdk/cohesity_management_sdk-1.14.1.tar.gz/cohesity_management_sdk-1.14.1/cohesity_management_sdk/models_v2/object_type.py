# -*- coding: utf-8 -*-


class ObjectType(object):

    """Implementation of the 'Object type.' model.

    Specifies Object type.

    Attributes:
        object_type (ObjectType4Enum): Specifies Object type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_type":'objectType'
    }

    def __init__(self,
                 object_type=None):
        """Constructor for the ObjectType class"""

        # Initialize members of the class
        self.object_type = object_type


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
        object_type = dictionary.get('objectType')

        # Return an object of this model
        return cls(object_type)


