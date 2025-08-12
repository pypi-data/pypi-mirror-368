# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.action_object_level_response

class ProtectedObjectActionResponse(object):

    """Implementation of the 'ProtectedObjectActionResponse' model.

    Specifies the response upon performing an action on protected objects.

    Attributes:
        action (Action5Enum): Specifies the action type to be performed on
            object getting protected. Based on selected action, provide the
            action params.
        objects (list of ActionObjectLevelResponse): Specifies the list of
            objects on which the provided action was performed.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "action":'action',
        "objects":'objects'
    }

    def __init__(self,
                 action=None,
                 objects=None):
        """Constructor for the ProtectedObjectActionResponse class"""

        # Initialize members of the class
        self.action = action
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
        action = dictionary.get('action')
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.action_object_level_response.ActionObjectLevelResponse.from_dictionary(structure))

        # Return an object of this model
        return cls(action,
                   objects)


