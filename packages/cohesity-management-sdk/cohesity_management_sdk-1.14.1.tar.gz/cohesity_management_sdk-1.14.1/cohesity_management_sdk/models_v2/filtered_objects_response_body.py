# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.filtered_object

class FilteredObjectsResponseBody(object):

    """Implementation of the 'FilteredObjectsResponseBody' model.

    Specifies the filter details.

    Attributes:
        filtered_objects (list of FilteredObject): Specifies the list of
            filtered Objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "filtered_objects":'filteredObjects'
    }

    def __init__(self,
                 filtered_objects=None):
        """Constructor for the FilteredObjectsResponseBody class"""

        # Initialize members of the class
        self.filtered_objects = filtered_objects


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
        filtered_objects = None
        if dictionary.get("filteredObjects") is not None:
            filtered_objects = list()
            for structure in dictionary.get('filteredObjects'):
                filtered_objects.append(cohesity_management_sdk.models_v2.filtered_object.FilteredObject.from_dictionary(structure))

        # Return an object of this model
        return cls(filtered_objects)


