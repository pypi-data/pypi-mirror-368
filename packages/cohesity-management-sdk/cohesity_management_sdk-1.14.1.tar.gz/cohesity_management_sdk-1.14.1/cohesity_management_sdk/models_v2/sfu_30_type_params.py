# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.fallback_option

class Sfu30TypeParams(object):

    """Implementation of the 'Sfu30TypeParams' model.

    Specifies the params for Sfu30 mapping type mapping.

    Attributes:
        fallback_option (FallbackOption): Specifies a fallback user id mapping
            param in case the primary config does not work.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "fallback_option":'fallbackOption'
    }

    def __init__(self,
                 fallback_option=None):
        """Constructor for the Sfu30TypeParams class"""

        # Initialize members of the class
        self.fallback_option = fallback_option


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
        fallback_option = cohesity_management_sdk.models_v2.fallback_option.FallbackOption.from_dictionary(dictionary.get('fallbackOption')) if dictionary.get('fallbackOption') else None

        # Return an object of this model
        return cls(fallback_option)


