# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.user
import cohesity_management_sdk.models_v2.tdm_clone_task_response_params

class TdmObjectTimelineEvent(object):

    """Implementation of the 'TdmObjectTimelineEvent' model.

    Specifies a TDM object timeline event.

    Attributes:
        id (string): Specifies the unique ID of the event.
        created_at (long|int): Specifies the time (in usecs from epoch) at
            which the event was created.
        created_by_user (User): Specifies the user, who triggered the event.
        status (Status12Enum): Specifies the current status of the event.
        error_message (string): Specifies the error message if the event is in
            failed state.
        description (string): Specifies the description of the event, as
            provided by the user.
        event_group_id (string): Specifies the ID of the group this event
            belongs to. Events with same group ID are considered to be a
            single timeline for the TDM object. Different group IDs mean
            different timelines for the TDM object.
        action (ActionEnum): Specifies the action for the event.
        clone_params (TdmCloneTaskResponseParams): Specifies the response
            parameters for a clone task.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "action":'action',
        "created_at":'createdAt',
        "created_by_user":'createdByUser',
        "status":'status',
        "error_message":'errorMessage',
        "description":'description',
        "event_group_id":'eventGroupId',
        "clone_params":'cloneParams'
    }

    def __init__(self,
                 id=None,
                 action=None,
                 created_at=None,
                 created_by_user=None,
                 status=None,
                 error_message=None,
                 description=None,
                 event_group_id=None,
                 clone_params=None):
        """Constructor for the TdmObjectTimelineEvent class"""

        # Initialize members of the class
        self.id = id
        self.created_at = created_at
        self.created_by_user = created_by_user
        self.status = status
        self.error_message = error_message
        self.description = description
        self.event_group_id = event_group_id
        self.action = action
        self.clone_params = clone_params


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
        created_at = dictionary.get('createdAt')
        created_by_user = cohesity_management_sdk.models_v2.user.User.from_dictionary(dictionary.get('createdByUser')) if dictionary.get('createdByUser') else None
        status = dictionary.get('status')
        error_message = dictionary.get('errorMessage')
        description = dictionary.get('description')
        event_group_id = dictionary.get('eventGroupId')
        clone_params = cohesity_management_sdk.models_v2.tdm_clone_task_response_params.TdmCloneTaskResponseParams.from_dictionary(dictionary.get('cloneParams')) if dictionary.get('cloneParams') else None

        # Return an object of this model
        return cls(id,
                   action,
                   created_at,
                   created_by_user,
                   status,
                   error_message,
                   description,
                   event_group_id,
                   clone_params)


