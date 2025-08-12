# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.entity_proto

class SANGroupEntityRecoverParams_SANVolumeRecoverParams(object):

    """Implementation of the 'SANGroupEntityRecoverParams_SANVolumeRecoverParams' model.

    Attributes:
        volume_entity (EntityProto): Entity proto of a volume.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "volume_entity":'volumeEntity'
    }

    def __init__(self,
                 volume_entity=None):
        """Constructor for the SANGroupEntityRecoverParams_SANVolumeRecoverParams class"""

        # Initialize members of the class
        self.volume_entity = volume_entity


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
        volume_entity = cohesity_management_sdk.models.entity_proto.EntityProto.from_dictionary(dictionary.get('volumeEntity')) if dictionary.get('volumeEntity') else None

        # Return an object of this model
        return cls(volume_entity)


