# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.nimble_protection_group_object_params

class NimbleProtectionGroupParams(object):

    """Implementation of the 'NimbleProtectionGroupParams' model.

    Specifies the parameters which are specific to Nimble related Protection
    Groups.

    Attributes:
        objects (list of NimbleProtectionGroupObjectParams): Specifies the
            objects to be included in the Protection Group.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "source_id":'sourceId',
        "source_name":'sourceName'
    }

    def __init__(self,
                 objects=None,
                 source_id=None,
                 source_name=None):
        """Constructor for the NimbleProtectionGroupParams class"""

        # Initialize members of the class
        self.objects = objects
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
                objects.append(cohesity_management_sdk.models_v2.nimble_protection_group_object_params.NimbleProtectionGroupObjectParams.from_dictionary(structure))
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')

        # Return an object of this model
        return cls(objects,
                   source_id,
                   source_name)


