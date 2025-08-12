# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.resume_action_object_level_response
import cohesity_management_sdk.models_v2.pause_action_object_level_response
import cohesity_management_sdk.models_v2.run_now_action_object_level_response
import cohesity_management_sdk.models_v2.unprotect_action_object_level_response

class ActionObjectLevelResponse(object):

    """Implementation of the 'ActionObjectLevelResponse' model.

    Specifies the object level response params after performing an action on a
    protected object.

    Attributes:
        id (long|int): Specifies the ID of the object.
        name (string): Specifies the name of the object.
        resume_status (ResumeActionObjectLevelResponse): Specifies the
            infomration about status of resume action.
        pause_status (PauseActionObjectLevelResponse): Specifies the
            infomration about status of pause action.
        run_now_status (RunNowActionObjectLevelResponse): Specifies the
            infomration about status of run now action.
        un_protect_status (UnprotectActionObjectLevelResponse): Specifies the
            infomration about status of Unprotect action.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "resume_status":'resumeStatus',
        "pause_status":'pauseStatus',
        "run_now_status":'runNowStatus',
        "un_protect_status":'unProtectStatus'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 resume_status=None,
                 pause_status=None,
                 run_now_status=None,
                 un_protect_status=None):
        """Constructor for the ActionObjectLevelResponse class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.resume_status = resume_status
        self.pause_status = pause_status
        self.run_now_status = run_now_status
        self.un_protect_status = un_protect_status


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
        id = dictionary.get('id')
        name = dictionary.get('name')
        resume_status = cohesity_management_sdk.models_v2.resume_action_object_level_response.ResumeActionObjectLevelResponse.from_dictionary(dictionary.get('resumeStatus')) if dictionary.get('resumeStatus') else None
        pause_status = cohesity_management_sdk.models_v2.pause_action_object_level_response.PauseActionObjectLevelResponse.from_dictionary(dictionary.get('pauseStatus')) if dictionary.get('pauseStatus') else None
        run_now_status = cohesity_management_sdk.models_v2.run_now_action_object_level_response.RunNowActionObjectLevelResponse.from_dictionary(dictionary.get('runNowStatus')) if dictionary.get('runNowStatus') else None
        un_protect_status = cohesity_management_sdk.models_v2.unprotect_action_object_level_response.UnprotectActionObjectLevelResponse.from_dictionary(dictionary.get('unProtectStatus')) if dictionary.get('unProtectStatus') else None

        # Return an object of this model
        return cls(id,
                   name,
                   resume_status,
                   pause_status,
                   run_now_status,
                   un_protect_status)


