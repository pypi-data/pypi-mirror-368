# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.action_object_mapping

class CommonObjectsActionParams(object):

    """Implementation of the 'CommonObjectsActionParams' model.

    Specifies the comon action params needed for performing bulk actions on
    list of objects.

    Attributes:
        object_map (list of ActionObjectMapping): Specifies the objectMap that
            will be used to perform bulk actions such as linking and
            unlinking.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_map":'objectMap'
    }

    def __init__(self,
                 object_map=None):
        """Constructor for the CommonObjectsActionParams class"""

        # Initialize members of the class
        self.object_map = object_map


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
        object_map = None
        if dictionary.get("objectMap") is not None:
            object_map = list()
            for structure in dictionary.get('objectMap'):
                object_map.append(cohesity_management_sdk.models_v2.action_object_mapping.ActionObjectMapping.from_dictionary(structure))

        # Return an object of this model
        return cls(object_map)


