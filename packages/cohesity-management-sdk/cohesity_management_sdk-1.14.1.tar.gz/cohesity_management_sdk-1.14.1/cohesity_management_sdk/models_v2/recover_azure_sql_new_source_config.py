# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recovery_object_identifier

class RecoverAzureSqlNewSourceConfig(object):

    """Implementation of the 'RecoverAzureSqlNewSourceConfig' model.

    Specifies the configuration for recovering Azure SQL instance to
      the new target.

    Attributes:
        source (RecoveryObjectIdentifier): Specifies the target source details where Azure SQL database
          will be recovered. This source id should be a Azure SQL target instance
          id were databases could be restored.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source":'source'
    }

    def __init__(self,
                 source=None):
        """Constructor for the RecoverAzureSqlNewSourceConfig class"""

        # Initialize members of the class
        self.source = source


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
        source = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None

        # Return an object of this model
        return cls(source)