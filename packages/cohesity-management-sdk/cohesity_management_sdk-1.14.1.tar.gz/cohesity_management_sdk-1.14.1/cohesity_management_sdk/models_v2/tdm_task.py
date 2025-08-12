# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.user
import cohesity_management_sdk.models_v2.tdm_clone_task_response_params
import cohesity_management_sdk.models_v2.tdm_refresh_task_response_params

class TdmTask(object):

    """Implementation of the 'TdmTask' model.

    Specifies a TDM task.

    Attributes:
        id (string): Specifies the unique ID of the task.
        start_time_usecs (long|int): Specifies the time (in usecs from epoch)
            when the task was started.
        end_time_usecs (long|int): Specifies the time (in usecs from epoch)
            when the task was completed.
        status (Status13Enum): Specifies the current status of the task.
        action (Action1Enum): Specifies the TDM Task action.
        created_by_user (User): Specifies the user, who created this task.
        clone_params (TdmCloneTaskResponseParams): Specifies the response
            parameters for a clone task.
        refresh_params (TdmRefreshTaskResponseParams): Specifies the response
            parameters for a refresh task.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "action":'action',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "status":'status',
        "created_by_user":'createdByUser',
        "clone_params":'cloneParams',
        "refresh_params":'refreshParams'
    }

    def __init__(self,
                 id=None,
                 action=None,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 status=None,
                 created_by_user=None,
                 clone_params=None,
                 refresh_params=None):
        """Constructor for the TdmTask class"""

        # Initialize members of the class
        self.id = id
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.status = status
        self.action = action
        self.created_by_user = created_by_user
        self.clone_params = clone_params
        self.refresh_params = refresh_params


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
        action = dictionary.get('action')
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')
        status = dictionary.get('status')
        created_by_user = cohesity_management_sdk.models_v2.user.User.from_dictionary(dictionary.get('createdByUser')) if dictionary.get('createdByUser') else None
        clone_params = cohesity_management_sdk.models_v2.tdm_clone_task_response_params.TdmCloneTaskResponseParams.from_dictionary(dictionary.get('cloneParams')) if dictionary.get('cloneParams') else None
        refresh_params = cohesity_management_sdk.models_v2.tdm_refresh_task_response_params.TdmRefreshTaskResponseParams.from_dictionary(dictionary.get('refreshParams')) if dictionary.get('refreshParams') else None

        # Return an object of this model
        return cls(id,
                   action,
                   start_time_usecs,
                   end_time_usecs,
                   status,
                   created_by_user,
                   clone_params,
                   refresh_params)


