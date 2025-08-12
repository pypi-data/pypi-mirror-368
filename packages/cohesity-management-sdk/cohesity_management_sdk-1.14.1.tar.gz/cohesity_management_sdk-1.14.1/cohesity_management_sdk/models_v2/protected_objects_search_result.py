# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protected_object
import cohesity_management_sdk.models_v2.metadata

class ProtectedObjectsSearchResult(object):

    """Implementation of the 'Protected Objects Search Result' model.

    Specifies the Protected Objects search result.

    Attributes:
        objects (list of ProtectedObject): Specifies the list of Protected
            Objects.
        metadata (Metadata): Specifies the metadata information about the
            Protection Groups, Protection Policy etc., for search result.
        num_results (long|int): Specifies the total number of search results
            which matches the search criteria.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "metadata":'metadata',
        "num_results":'numResults'
    }

    def __init__(self,
                 objects=None,
                 metadata=None,
                 num_results=None):
        """Constructor for the ProtectedObjectsSearchResult class"""

        # Initialize members of the class
        self.objects = objects
        self.metadata = metadata
        self.num_results = num_results


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
                objects.append(cohesity_management_sdk.models_v2.protected_object.ProtectedObject.from_dictionary(structure))
        metadata = cohesity_management_sdk.models_v2.metadata.Metadata.from_dictionary(dictionary.get('metadata')) if dictionary.get('metadata') else None
        num_results = dictionary.get('numResults')

        # Return an object of this model
        return cls(objects,
                   metadata,
                   num_results)


