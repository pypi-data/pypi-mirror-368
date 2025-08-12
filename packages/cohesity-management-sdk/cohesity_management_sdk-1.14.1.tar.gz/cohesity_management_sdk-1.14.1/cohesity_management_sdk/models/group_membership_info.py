# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class GroupMembershipInfo(object):

    """Implementation of the 'GroupMembershipInfo' model.

    Attributes:
        entity_id (long| int): Specifies the entity Id of the Group.
        graph_uuid (string): Specifies the Graph UUID of the Group.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "entity_id": 'entityId',
        "graph_uuid": 'graphUuid'
    }

    def __init__(self,
                 entity_id=None,
                 graph_uuid=None):
        """Constructor for the GroupMembershipInfo class"""

        # Initialize members of the class
        self.entity_id = entity_id
        self.graph_uuid = graph_uuid


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
        entity_id = dictionary.get('entityId', None)
        graph_uuid = dictionary.get('graphUuid', None)

        # Return an object of this model
        return cls(entity_id,
                   graph_uuid)


