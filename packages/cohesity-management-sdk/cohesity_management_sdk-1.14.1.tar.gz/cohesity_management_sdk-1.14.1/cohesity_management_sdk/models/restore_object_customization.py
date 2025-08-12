# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.restored_object_network_config_proto

class RestoreObjectCustomization(object):

    """Implementation of the 'RestoreObjectCustomization' model.

    Proto to specify the restore object customization.

    Attributes:
        entity_id (int): Represents the Entity id of the object for
            which below customizations are populated.
        network_config (RestoredObjectNetworkConfigProto): Indicates the Network configuration
            for the restore object.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "entity_id":'entityId',
        "network_config":'networkConfig'
    }

    def __init__(self,
                 entity_id=None,
                 network_config=None):
        """Constructor for the RestoreObjectState class"""

        # Initialize members of the class
        self.entity_id = entity_id
        self.network_config = network_config


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
        entity_id = dictionary.get('entityId')
        network_config = cohesity_management_sdk.models.restored_object_network_config_proto.RestoredObjectNetworkConfigProto.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None

        # Return an object of this model
        return cls(entity_id,
                   network_config)