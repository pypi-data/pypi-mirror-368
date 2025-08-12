# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.nis_provider

class NisProviders(object):

    """Implementation of the 'NisProviders' model.

    Response of NIS Providers.

    Attributes:
        nis_providers (list of NisProvider): A list of NIS Providers.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "nis_providers":'nisProviders'
    }

    def __init__(self,
                 nis_providers=None):
        """Constructor for the NisProviders class"""

        # Initialize members of the class
        self.nis_providers = nis_providers


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
        nis_providers = None
        if dictionary.get("nisProviders") is not None:
            nis_providers = list()
            for structure in dictionary.get('nisProviders'):
                nis_providers.append(cohesity_management_sdk.models_v2.nis_provider.NisProvider.from_dictionary(structure))

        # Return an object of this model
        return cls(nis_providers)


