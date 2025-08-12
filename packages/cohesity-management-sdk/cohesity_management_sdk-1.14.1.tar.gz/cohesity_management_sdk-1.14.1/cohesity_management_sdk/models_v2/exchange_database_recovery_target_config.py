# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source_14

class ExchangeDatabaseRecoveryTargetConfig(object):

    """Implementation of the 'Exchange database Recovery Target Config.' model.

    Specifies the target object parameters to recover Exchange database.

    Attributes:
        source (Source14): Specifies the id of the physical source to which
            the exchange database will be recovered.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source":'source'
    }

    def __init__(self,
                 source=None):
        """Constructor for the ExchangeDatabaseRecoveryTargetConfig class"""

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
        source = cohesity_management_sdk.models_v2.source_14.Source14.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None

        # Return an object of this model
        return cls(source)


