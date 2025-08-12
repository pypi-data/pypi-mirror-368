# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protection_group_alerting_policy
import cohesity_management_sdk.models_v2.data_tiering_source
import cohesity_management_sdk.models_v2.data_tiering_target
import cohesity_management_sdk.models_v2.data_tiering_schedule
import cohesity_management_sdk.models_v2.data_tiering_task_run

class CommonDataTieringTaskResponse(object):

    """Implementation of the 'CommonDataTieringTaskResponse' model.

    Specifies the data tiering task details.

    Attributes:
        id (string): Specifies the id of the data tiering task.
        name (string): Specifies the name of the data tiering task.
        description (string): Specifies a description of the data tiering
            task.
        alert_policy (ProtectionGroupAlertingPolicy): Specifies a policy for
            alerting users of the status of a Protection Group.
        source (DataTieringSource): Specifies the source data tiering
            details.
        target (DataTieringTarget): Specifies the target data tiering
            details.
        schedule (DataTieringSchedule): Specifies the data tiering schedule.
        mtype (Type12Enum): Type of data tiering task. 'Downtier' indicates
            downtiering task. 'Uptier' indicates uptiering task.
        last_run (DataTieringTaskRun): Specifies the data tiering task run.
        is_active (bool): Whether the data tiering task is active or not.
        is_paused (bool): Whether the data tiering task is paused. New runs
            are not scheduled for the paused tasks. Active run of the task (if
            any) is not impacted.
        is_deleted (bool): Tracks whether the backup job has actually been
            deleted.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "mtype":'type',
        "id":'id',
        "description":'description',
        "alert_policy":'alertPolicy',
        "source":'source',
        "target":'target',
        "schedule":'schedule',
        "last_run":'lastRun',
        "is_active":'isActive',
        "is_paused":'isPaused',
        "is_deleted":'isDeleted'
    }

    def __init__(self,
                 name=None,
                 mtype=None,
                 id=None,
                 description=None,
                 alert_policy=None,
                 source=None,
                 target=None,
                 schedule=None,
                 last_run=None,
                 is_active=True,
                 is_paused=True,
                 is_deleted=True):
        """Constructor for the CommonDataTieringTaskResponse class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.description = description
        self.alert_policy = alert_policy
        self.source = source
        self.target = target
        self.schedule = schedule
        self.mtype = mtype
        self.last_run = last_run
        self.is_active = is_active
        self.is_paused = is_paused
        self.is_deleted = is_deleted


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
        name = dictionary.get('name')
        mtype = dictionary.get('type')
        id = dictionary.get('id')
        description = dictionary.get('description')
        alert_policy = cohesity_management_sdk.models_v2.protection_group_alerting_policy.ProtectionGroupAlertingPolicy.from_dictionary(dictionary.get('alertPolicy')) if dictionary.get('alertPolicy') else None
        source = cohesity_management_sdk.models_v2.data_tiering_source.DataTieringSource.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None
        target = cohesity_management_sdk.models_v2.data_tiering_target.DataTieringTarget.from_dictionary(dictionary.get('target')) if dictionary.get('target') else None
        schedule = cohesity_management_sdk.models_v2.data_tiering_schedule.DataTieringSchedule.from_dictionary(dictionary.get('schedule')) if dictionary.get('schedule') else None
        last_run = cohesity_management_sdk.models_v2.data_tiering_task_run.DataTieringTaskRun.from_dictionary(dictionary.get('lastRun')) if dictionary.get('lastRun') else None
        is_active = dictionary.get("isActive") if dictionary.get("isActive") else True
        is_paused = dictionary.get("isPaused") if dictionary.get("isPaused") else True
        is_deleted = dictionary.get("isDeleted") if dictionary.get("isDeleted") else True

        # Return an object of this model
        return cls(name,
                   mtype,
                   id,
                   description,
                   alert_policy,
                   source,
                   target,
                   schedule,
                   last_run,
                   is_active,
                   is_paused,
                   is_deleted)


