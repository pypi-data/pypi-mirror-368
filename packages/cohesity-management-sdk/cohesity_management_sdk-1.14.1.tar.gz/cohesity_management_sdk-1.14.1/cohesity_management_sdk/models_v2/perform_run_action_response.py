# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.cancel_protection_group_run_response_params
import cohesity_management_sdk.models_v2.pause_protection_run_action_response_params
import cohesity_management_sdk.models_v2.resume_protection_run_action_response_params

class PerformRunActionResponse(object):

    """Implementation of the 'PerformRunActionResponse' model.

    Specifies the response of the performed run action.

    Attributes:
        action (Action9Enum): Specifies the type of the action is performed on
            protection runs.
        cancel_params (list of CancelProtectionGroupRunResponseParams): Specifies the
            cancel action response params.
        pause_params (list of PauseProtectionRunActionResponseParams): Specifies the pause
            action response params.
        resume_params (list of ResumeProtectionRunActionResponseParams): Specifies the resume
            action response params.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "action":'action',
        "cancel_params":'cancelParams',
        "pause_params":'pauseParams',
        "resume_params":'resumeParams'
    }

    def __init__(self,
                 action=None,
                 cancel_params=None,
                 pause_params=None,
                 resume_params=None):
        """Constructor for the PerformRunActionResponse class"""

        # Initialize members of the class
        self.action = action
        self.cancel_params = cancel_params
        self.pause_params = pause_params
        self.resume_params = resume_params


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
        cancel_params = None
        if dictionary.get("cancelParams") is not None:
            cancel_params = list()
            for structure in dictionary.get('cancelParams'):
                cancel_params.append(cohesity_management_sdk.models_v2.cancel_protection_group_run_response_params.CancelProtectionGroupRunResponseParams.from_dictionary(structure))
        pause_params = None
        if dictionary.get("pauseParams") is not None:
            pause_params = list()
            for structure in dictionary.get('pauseParams'):
                pause_params.append(cohesity_management_sdk.models_v2.pause_protection_run_action_response_params.PauseProtectionRunActionResponseParams.from_dictionary(structure))
        resume_params = None
        if dictionary.get("resumeParams") is not None:
            resume_params = list()
            for structure in dictionary.get('resumeParams'):
                resume_params.append(cohesity_management_sdk.models_v2.resume_protection_run_action_response_params.ResumeProtectionRunActionResponseParams.from_dictionary(structure))

        # Return an object of this model
        return cls(action,
                   cancel_params,
                   pause_params,
                   resume_params)


