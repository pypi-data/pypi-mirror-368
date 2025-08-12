# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_objects_action_params

class ObjectsActionRequest(object):

    """Implementation of the 'ObjectsActionRequest' model.

    Specifies the type of the action need to be performed on given set of
    objects.

    Attributes:
        action (Action4Enum): Specifies the action type that need to be
            performed.
        link_params (CommonObjectsActionParams): Specifies the parameters
            required for linking objects. This is currently used as a part of
            vm migration workflow.
        un_link_params (CommonObjectsActionParams): Specifies the parameters
            required for unlinking objects. This is currently used as a part
            of vm migration workflow.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "action":'action',
        "link_params":'linkParams',
        "un_link_params":'unLinkParams'
    }

    def __init__(self,
                 action=None,
                 link_params=None,
                 un_link_params=None):
        """Constructor for the ObjectsActionRequest class"""

        # Initialize members of the class
        self.action = action
        self.link_params = link_params
        self.un_link_params = un_link_params


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
        link_params = cohesity_management_sdk.models_v2.common_objects_action_params.CommonObjectsActionParams.from_dictionary(dictionary.get('linkParams')) if dictionary.get('linkParams') else None
        un_link_params = cohesity_management_sdk.models_v2.common_objects_action_params.CommonObjectsActionParams.from_dictionary(dictionary.get('unLinkParams')) if dictionary.get('unLinkParams') else None

        # Return an object of this model
        return cls(action,
                   link_params,
                   un_link_params)


