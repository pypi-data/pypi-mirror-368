# -*- coding: utf-8 -*-


class AuditLogsEntityTypes(object):

    """Implementation of the 'AuditLogsEntityTypes' model.

    Specifies entity types of audit logs.

    Attributes:
        entity_types (list of string): Specifies a list of audit logs entity
            types.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "entity_types":'entityTypes'
    }

    def __init__(self,
                 entity_types=None):
        """Constructor for the AuditLogsEntityTypes class"""

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


