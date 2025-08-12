# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.active_directory_protection_group_object_params
import cohesity_management_sdk.models_v2.indexing_policy

class ActiveDirectoryADProtectionGroupParameters(object):

    """Implementation of the 'Active Directory(AD) Protection Group Parameters.' model.

    Specifies the parameters which are specific to Active directory related
    Protection Groups.

    Attributes:
        objects (list of ActiveDirectoryProtectionGroupObjectParams):
            Specifies the list of object ids to be protected.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "indexing_policy":'indexingPolicy'
    }

    def __init__(self,
                 objects=None,
                 indexing_policy=None):
        """Constructor for the ActiveDirectoryADProtectionGroupParameters class"""

        # Initialize members of the class
        self.objects = objects
        self.indexing_policy = indexing_policy


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
                objects.append(cohesity_management_sdk.models_v2.active_directory_protection_group_object_params.ActiveDirectoryProtectionGroupObjectParams.from_dictionary(structure))
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None

        # Return an object of this model
        return cls(objects,
                   indexing_policy)


