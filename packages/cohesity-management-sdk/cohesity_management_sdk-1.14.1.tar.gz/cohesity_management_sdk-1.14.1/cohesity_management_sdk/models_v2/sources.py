# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protection_source

class Sources(object):

    """Implementation of the 'Sources' model.

    Protection Sources.

    Attributes:
        sources (list of ProtectionSource): Specifies the list of Protection
            Sources.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "sources":'sources'
    }

    def __init__(self,
                 sources=None):
        """Constructor for the Sources class"""

        # Initialize members of the class
        self.sources = sources


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
        sources = None
        if dictionary.get("sources") is not None:
            sources = list()
            for structure in dictionary.get('sources'):
                sources.append(cohesity_management_sdk.models_v2.protection_source.ProtectionSource.from_dictionary(structure))

        # Return an object of this model
        return cls(sources)


