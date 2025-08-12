# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protected_object_pause_action_params
import cohesity_management_sdk.models_v2.protected_object_resume_action_params
import cohesity_management_sdk.models_v2.protected_object_run_now_action_params
import cohesity_management_sdk.models_v2.protected_object_un_protect_action_params

class ProtectdObjectsActionRequest(object):

    """Implementation of the 'ProtectdObjectsActionRequest' model.

    Specifies the request for performing various actions on protected
    objects.

    Attributes:
        action (Action5Enum): Specifies the action type to be performed on
            object getting protected. Based on selected action, provide the
            action params.
        pause_params (ProtectedObjectPauseActionParams): Specifies the request
            parameters for Pause action on Protected objects.
        resume_params (ProtectedObjectResumeActionParams): Specifies the
            request parameters for Resume action on Protected objects.
        run_now_params (ProtectedObjectRunNowActionParams): Specifies the
            request parameters for RunNow action on Protected objects.
        un_protect_params (ProtectedObjectUnProtectActionParams): Specifies
            the request parameters for Unprotect action on Protected objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "action":'action',
        "pause_params":'pauseParams',
        "resume_params":'resumeParams',
        "run_now_params":'runNowParams',
        "un_protect_params":'unProtectParams'
    }

    def __init__(self,
                 action=None,
                 pause_params=None,
                 resume_params=None,
                 run_now_params=None,
                 un_protect_params=None):
        """Constructor for the ProtectdObjectsActionRequest class"""

        # Initialize members of the class
        self.action = action
        self.pause_params = pause_params
        self.resume_params = resume_params
        self.run_now_params = run_now_params
        self.un_protect_params = un_protect_params


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
        pause_params = cohesity_management_sdk.models_v2.protected_object_pause_action_params.ProtectedObjectPauseActionParams.from_dictionary(dictionary.get('pauseParams')) if dictionary.get('pauseParams') else None
        resume_params = cohesity_management_sdk.models_v2.protected_object_resume_action_params.ProtectedObjectResumeActionParams.from_dictionary(dictionary.get('resumeParams')) if dictionary.get('resumeParams') else None
        run_now_params = cohesity_management_sdk.models_v2.protected_object_run_now_action_params.ProtectedObjectRunNowActionParams.from_dictionary(dictionary.get('runNowParams')) if dictionary.get('runNowParams') else None
        un_protect_params = cohesity_management_sdk.models_v2.protected_object_un_protect_action_params.ProtectedObjectUnProtectActionParams.from_dictionary(dictionary.get('unProtectParams')) if dictionary.get('unProtectParams') else None

        # Return an object of this model
        return cls(action,
                   pause_params,
                   resume_params,
                   run_now_params,
                   un_protect_params)


