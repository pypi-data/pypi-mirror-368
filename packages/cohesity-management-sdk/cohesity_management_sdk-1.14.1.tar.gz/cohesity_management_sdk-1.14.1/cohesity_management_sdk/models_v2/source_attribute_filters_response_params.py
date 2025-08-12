# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source_attribute_filter

class SourceAttributeFiltersResponseParams(object):

    """Implementation of the 'SourceAttributeFiltersResponseParams' model.

    Protection Source attribute filters

    Attributes:
        source_attribute_filters (list of SourceAttributeFilter): Specifies
            the list of protection source filters.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_attribute_filters":'sourceAttributeFilters'
    }

    def __init__(self,
                 source_attribute_filters=None):
        """Constructor for the SourceAttributeFiltersResponseParams class"""

        # Initialize members of the class
        self.source_attribute_filters = source_attribute_filters


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
        source_attribute_filters = None
        if dictionary.get("sourceAttributeFilters") is not None:
            source_attribute_filters = list()
            for structure in dictionary.get('sourceAttributeFilters'):
                source_attribute_filters.append(cohesity_management_sdk.models_v2.source_attribute_filter.SourceAttributeFilter.from_dictionary(structure))

        # Return an object of this model
        return cls(source_attribute_filters)


