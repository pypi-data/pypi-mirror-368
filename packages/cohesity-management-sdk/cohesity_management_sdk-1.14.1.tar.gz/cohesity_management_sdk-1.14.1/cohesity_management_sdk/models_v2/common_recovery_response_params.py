# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.tenant
import cohesity_management_sdk.models_v2.creation_info
import cohesity_management_sdk.models_v2.common_filter_expression
import cohesity_management_sdk.models_v2.retrieve_archive_task

class CommonRecoveryResponseParams(object):

    """Implementation of the 'Common Recovery Response Params.' model.

    Specifies the common response parameters to create a Recovery

    Attributes:
        id (string): Specifies the id of the Recovery.
        name (string): Specifies the name of the Recovery.
        is_multi_stage_restore (bool): Specifies whether the current recovery operation is a multi-stage
          restore operation. This is currently used by VMware recoveres for the migration/hot-standby
          use case.
        is_parent_recovery (bool): Specifies whether the current recovery operation has created
          child recoveries. This is currently used in SQL recovery where multiple
          child recoveries can be tracked under a common/parent recovery.
        start_time_usecs (long|int): Specifies the start time of the Recovery
            in Unix timestamp epoch in microseconds.
        end_time_usecs (long|int): Specifies the end time of the Recovery in
            Unix timestamp epoch in microseconds. This field will be populated
            only after Recovery is finished.
        filter_params (CommonFilterExpression): Specifies the params for filtering the entity to be recovered.
          Depending on the recovery type, this can be used to filter the items within
          an entity or the entities themselves.
        status (Status6Enum): Status of the Recovery. 'Running' indicates that
            the Recovery is still running. 'Canceled' indicates that the
            Recovery has been cancelled. 'Canceling' indicates that the
            Recovery is in the process of being cancelled. 'Failed' indicates
            that the Recovery has failed. 'Succeeded' indicates that the
            Recovery has finished successfully. 'SucceededWithWarning'
            indicates that the Recovery finished successfully, but there were
            some warning messages.
        progress_task_id (string): Progress monitor task id for Recovery.
        snapshot_environment (SnapshotEnvironment1Enum): Specifies the type of
            snapshot environment for which the Recovery was performed.
        recovery_action (RecoveryActionEnum): Specifies the type of recover
            action.
        parent_recovery_id (string): If current recovery is child recovery triggered by another parent
          recovery operation, then this field willt specify the id of the parent recovery.
        permissions (list of Tenant): Specifies the list of tenants that have
            permissions for this recovery.
        creation_info (CreationInfo): Specifies the information about the
            creation of the protection group or recovery.
        can_tear_down (bool): Specifies whether it's possible to tear down the
            objects created by the recovery.
        tear_down_status (TearDownStatus3Enum): Specifies the status of the
            tear down operation. This is only set when the canTearDown is set
            to true. 'DestroyScheduled' indicates that the tear down is ready
            to schedule. 'Destroying' indicates that the tear down is still
            running. 'Destroyed' indicates that the tear down succeeded.
            'DestroyError' indicates that the tear down failed.
        tear_down_message (string): Specifies the error message about the tear
            down operation if it fails.
        messages (list of string): Specifies messages about the recovery.
        retrieve_archive_tasks (list of RetrieveArchiveTask): Specifies the list of persistent state of a retrieve of an archive
          task.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "is_multi_stage_restore":'isMultiStageRestore',
        "is_parent_recovery":'isParentRecovery',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "filter_params":'filterParams',
        "status":'status',
        "progress_task_id":'progressTaskId',
        "snapshot_environment":'snapshotEnvironment',
        "recovery_action":'recoveryAction',
        "parent_recovery_id":'parentRecoveryId',
        "permissions":'permissions',
        "creation_info":'creationInfo',
        "can_tear_down":'canTearDown',
        "tear_down_status":'tearDownStatus',
        "tear_down_message":'tearDownMessage',
        "messages":'messages',
        "retrieve_archive_tasks":'retrieveArchiveTasks'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 is_multi_stage_restore=None,
                 is_parent_recovery=None,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 filter_params=None,
                 status=None,
                 progress_task_id=None,
                 snapshot_environment=None,
                 recovery_action=None,
                 parent_recovery_id=None,
                 permissions=None,
                 creation_info=None,
                 can_tear_down=None,
                 tear_down_status=None,
                 tear_down_message=None,
                 messages=None,
                 retrieve_archive_tasks=None):
        """Constructor for the CommonRecoveryResponseParams class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.is_multi_stage_restore = is_multi_stage_restore
        self.is_parent_recovery = is_parent_recovery
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.filter_params = filter_params
        self.status = status
        self.progress_task_id = progress_task_id
        self.snapshot_environment = snapshot_environment
        self.recovery_action = recovery_action
        self.parent_recovery_id = parent_recovery_id
        self.permissions = permissions
        self.creation_info = creation_info
        self.can_tear_down = can_tear_down
        self.tear_down_status = tear_down_status
        self.tear_down_message = tear_down_message
        self.messages = messages
        self.retrieve_archive_tasks = retrieve_archive_tasks


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
        is_multi_stage_restore = dictionary.get('isMultiStageRestore')
        is_parent_recovery = dictionary.get('isParentRecovery')
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')
        filter_params = cohesity_management_sdk.models_v2.common_filter_expression.CommonFilterExpression.from_dictionary(
            dictionary.get('filterParams')) if dictionary.get('filterParams') else None
        status = dictionary.get('status')
        progress_task_id = dictionary.get('progressTaskId')
        snapshot_environment = dictionary.get('snapshotEnvironment')
        recovery_action = dictionary.get('recoveryAction')
        parent_recovery_id = dictionary.get('parentRecoveryId')
        permissions = None
        if dictionary.get("permissions") is not None:
            permissions = list()
            for structure in dictionary.get('permissions'):
                permissions.append(cohesity_management_sdk.models_v2.tenant.Tenant.from_dictionary(structure))
        creation_info = cohesity_management_sdk.models_v2.creation_info.CreationInfo.from_dictionary(dictionary.get('creationInfo')) if dictionary.get('creationInfo') else None
        can_tear_down = dictionary.get('canTearDown')
        tear_down_status = dictionary.get('tearDownStatus')
        tear_down_message = dictionary.get('tearDownMessage')
        messages = dictionary.get('messages')
        retrieve_archive_tasks = None
        if dictionary.get('retrieveArchiveTasks') is not None:
            retrieve_archive_tasks = list()
            for structure in dictionary.get('retrieveArchiveTasks'):
                retrieve_archive_tasks.append(cohesity_management_sdk.models_v2.retrieve_archive_task.RetrieveArchiveTask.from_dictionary(structure))

        # Return an object of this model
        return cls(id,
                   name,
                   is_multi_stage_restore,
                   is_parent_recovery,
                   start_time_usecs,
                   end_time_usecs,
                   filter_params,
                   status,
                   progress_task_id,
                   snapshot_environment,
                   recovery_action,
                   parent_recovery_id,
                   permissions,
                   creation_info,
                   can_tear_down,
                   tear_down_status,
                   tear_down_message,
                   messages,
                   retrieve_archive_tasks)