# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.rigel_registration_config

class HeliosRegistrationConfig(object):

    """Implementation of the 'Helios Registration Config.' model.

    Specifies the Helios Registration Config.

    Attributes:
        entity_type (EntityType2Enum): Specifies the type of entity that is
            registered on Helios.
        rigel_reg_config (RigelRegistrationConfig): Specifies the Rigel
            Registration Config.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "entity_type":'entityType',
        "rigel_reg_config":'rigelRegConfig'
    }

    def __init__(self,
                 entity_type=None,
                 rigel_reg_config=None):
        """Constructor for the HeliosRegistrationConfig class"""

        # Initialize members of the class
        self.entity_type = entity_type
        self.rigel_reg_config = rigel_reg_config


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
        entity_type = dictionary.get('entityType')
        rigel_reg_config = cohesity_management_sdk.models_v2.rigel_registration_config.RigelRegistrationConfig.from_dictionary(dictionary.get('rigelRegConfig')) if dictionary.get('rigelRegConfig') else None

        # Return an object of this model
        return cls(entity_type,
                   rigel_reg_config)


