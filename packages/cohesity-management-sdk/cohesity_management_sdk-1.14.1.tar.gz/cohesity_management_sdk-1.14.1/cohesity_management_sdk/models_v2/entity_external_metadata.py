# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.maintenance_mode_config

class EntityExternalMetadata(object):

    """Implementation of the 'EntityExternalMetadata' model.

    Specifies the External metadata of an entity

    Attributes:
        maintenance_mode_config (Type43Enum): Specifies the entity metadata for maintenance mode.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "maintenance_mode_config":'maintenanceModeConfig'
    }

    def __init__(self,
                 maintenance_mode_config=None):
        """Constructor for the EntityExternalMetadata class"""

        # Initialize members of the class
        self.maintenance_mode_config = maintenance_mode_config


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
        maintenance_mode_config = cohesity_management_sdk.models_v2.maintenance_mode_config.MaintenanceModeConfig.from_dictionary(
            dictionary.get('maintenanceModeConfig')) if dictionary.get('maintenanceModeConfig') else None

        # Return an object of this model
        return cls(maintenance_mode_config)