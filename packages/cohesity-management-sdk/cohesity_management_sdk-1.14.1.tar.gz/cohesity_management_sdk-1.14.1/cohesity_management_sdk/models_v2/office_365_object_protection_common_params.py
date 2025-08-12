# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.microsoft_365_object_protection_object_params
import cohesity_management_sdk.models_v2.indexing_policy

class Office365ObjectProtectionCommonParams(object):

    """Implementation of the 'Office365ObjectProtectionCommonParams' model.

    Specifies the parameters which are specific to Microsoft 365 Object
    Protection.

    Attributes:
        objects (list of Microsoft365ObjectProtectionObjectParams): Specifies
            the objects to be included in the Object Protection.
        exclude_object_ids (list of long|int): Specifies the objects to be
            excluded in the Object Protection.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "exclude_object_ids":'excludeObjectIds',
        "indexing_policy":'indexingPolicy',
        "source_id":'sourceId',
        "source_name":'sourceName'
    }

    def __init__(self,
                 objects=None,
                 exclude_object_ids=None,
                 indexing_policy=None,
                 source_id=None,
                 source_name=None):
        """Constructor for the Office365ObjectProtectionCommonParams class"""

        # Initialize members of the class
        self.objects = objects
        self.exclude_object_ids = exclude_object_ids
        self.indexing_policy = indexing_policy
        self.source_id = source_id
        self.source_name = source_name


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
                objects.append(cohesity_management_sdk.models_v2.microsoft_365_object_protection_object_params.Microsoft365ObjectProtectionObjectParams.from_dictionary(structure))
        exclude_object_ids = dictionary.get('excludeObjectIds')
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')

        # Return an object of this model
        return cls(objects,
                   exclude_object_ids,
                   indexing_policy,
                   source_id,
                   source_name)


