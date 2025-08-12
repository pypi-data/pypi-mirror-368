# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source_hierarchy_object_summaries

class ObjectSummaries(object):

    """Implementation of the 'ObjectSummaries' model.

    Specifies a list of Source Hierarchy Object Summaries.

    Attributes:
        objects (list of SourceHierarchyObjectSummaries): Specifies a list of
            Source Hierarchy Object summaries.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects'
    }

    def __init__(self,
                 objects=None):
        """Constructor for the ObjectSummaries class"""

        # Initialize members of the class
        self.objects = objects


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
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.source_hierarchy_object_summaries.SourceHierarchyObjectSummaries.from_dictionary(structure))

        # Return an object of this model
        return cls(objects)


