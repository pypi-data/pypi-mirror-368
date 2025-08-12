# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.tdm_clone_task_request_params
import cohesity_management_sdk.models_v2.tdm_snapshot_task_params
import cohesity_management_sdk.models_v2.tdm_refresh_task_request_params
import cohesity_management_sdk.models_v2.tdm_teardown_task_request_params

class CreateTdmTaskRequest(object):

    """Implementation of the 'CreateTdmTaskRequest' model.

    Specifies the request parameters to create a TDM task.

    Attributes:
        action (Action1Enum): Specifies the TDM Task action.
        clone_params (TdmCloneTaskRequestParams): Specifies the request
            parameters to create a clone task.
        snapshot_params (TdmSnapshotTaskParams): Specifies the parameters to
            create a snapshot of an existing clone.
        refresh_params (TdmRefreshTaskRequestParams): Specifies the parameters
            to refresh a clone with new data.
        teardown_params (TdmTeardownTaskRequestParams): Specifies the
            parameters to teardown a clone.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "action":'action',
        "clone_params":'cloneParams',
        "snapshot_params":'snapshotParams',
        "refresh_params":'refreshParams',
        "teardown_params":'teardownParams'
    }

    def __init__(self,
                 action=None,
                 clone_params=None,
                 snapshot_params=None,
                 refresh_params=None,
                 teardown_params=None):
        """Constructor for the CreateTdmTaskRequest class"""

        # Initialize members of the class
        self.action = action
        self.clone_params = clone_params
        self.snapshot_params = snapshot_params
        self.refresh_params = refresh_params
        self.teardown_params = teardown_params


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
        clone_params = cohesity_management_sdk.models_v2.tdm_clone_task_request_params.TdmCloneTaskRequestParams.from_dictionary(dictionary.get('cloneParams')) if dictionary.get('cloneParams') else None
        snapshot_params = cohesity_management_sdk.models_v2.tdm_snapshot_task_params.TdmSnapshotTaskParams.from_dictionary(dictionary.get('snapshotParams')) if dictionary.get('snapshotParams') else None
        refresh_params = cohesity_management_sdk.models_v2.tdm_refresh_task_request_params.TdmRefreshTaskRequestParams.from_dictionary(dictionary.get('refreshParams')) if dictionary.get('refreshParams') else None
        teardown_params = cohesity_management_sdk.models_v2.tdm_teardown_task_request_params.TdmTeardownTaskRequestParams.from_dictionary(dictionary.get('teardownParams')) if dictionary.get('teardownParams') else None

        # Return an object of this model
        return cls(action,
                   clone_params,
                   snapshot_params,
                   refresh_params,
                   teardown_params)


