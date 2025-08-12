# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.string_entity_ids


class ObjectStringIdentifier(object):

    """Implementation of the 'ObjectStringIdentifier' model.

    Specifies an ID generated to uniquely identify an entity.

    Attributes:
        int_id (int): Specifies the unique integer entity id.
          This is unique across one cluster. Two different Cohesity clusters may have
          same int_id for two different entities.
        string_ids (StringEntityIds): Specifies the string entity id generated for the given entity.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "int_id":'intId',
        "string_ids":'stringIds'
    }

    def __init__(self,
                 int_id=None,
                 string_ids=None):
        """Constructor for the ObjectStringIdentifier class"""

        # Initialize members of the class
        self.int_id = int_id
        self.string_ids = string_ids


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
        int_id = dictionary.get('intId')
        string_ids = cohesity_management_sdk.models.string_entity_ids.StringEntityIds.from_dictionary(dictionary.get('stringIds')) if dictionary.get('stringIds') else None

        # Return an object of this model
        return cls(int_id,
                   string_ids)