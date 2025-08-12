# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.cancel_protection_group_run_request
import cohesity_management_sdk.models_v2.pause_protection_run_action_params
import cohesity_management_sdk.models_v2.resume_protection_run_action_params

class PerformActionOnProtectionGroupRunRequest(object):

    """Implementation of the 'PerformActionOnProtectionGroupRunRequest' model.

    Specifies the request to perform actions on protection runs.
    cp action_enum.py perform_action_on_protection_group_run_request_action_enum.py


    Attributes:
        action (Action9Enum): Specifies the type of the action which will be
            performed on protection runs.
        cancel_params (list of CancelProtectionGroupRunRequest): Specifies the
            cancel action params for a protection run.
        pause_params (list of PauseProtectionRunActionParams): Specifies the pause
            action params for a protection run.
        resume_params (list of ResumeProtectionRunActionParams): Specifies the resume
            action params for a protection run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "action":'action',
        "cancel_params":'cancelParams',
        "pause_params":'pauseParams',
        "resume_params":'resumeParams'
    }

    def __init__(self,
                 action,
                 cancel_params=None,
                 pause_params=None,
                 resume_params=None):
        """Constructor for the PerformActionOnProtectionGroupRunRequest class"""

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
                cancel_params.append(cohesity_management_sdk.models_v2.cancel_protection_group_run_request.CancelProtectionGroupRunRequest.from_dictionary(structure))
        pause_params = None
        if dictionary.get("pauseParams") is not None:
            pause_params = list()
            for structure in dictionary.get('pauseParams'):
                pause_params.append(cohesity_management_sdk.models_v2.pause_protection_run_action_params.PauseProtectionRunActionParams.from_dictionary(structure))
        resume_params = None
        if dictionary.get("resumeParams") is not None:
            resume_params = list()
            for structure in dictionary.get('resumeParams'):
                resume_params.append(cohesity_management_sdk.models_v2.resume_protection_run_action_params.ResumeProtectionRunActionParams.from_dictionary(structure))

        # Return an object of this model
        return cls(action,
                   cancel_params,
                   pause_params,
                   resume_params)


