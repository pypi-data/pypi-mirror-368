# -*- coding: utf-8 -*-


class EntityTypes(object):

    """Implementation of the 'Entity Types' model.

    Entity Types

    Attributes:
        entity_types (EntityTypes1Enum): Entity Types

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "entity_types":'entityTypes'
    }

    def __init__(self,
                 entity_types=None):
        """Constructor for the EntityTypes class"""

        # Initialize members of the class
        self.entity_types = entity_types


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
        entity_types = dictionary.get('entityTypes')

        # Return an object of this model
        return cls(entity_types)


