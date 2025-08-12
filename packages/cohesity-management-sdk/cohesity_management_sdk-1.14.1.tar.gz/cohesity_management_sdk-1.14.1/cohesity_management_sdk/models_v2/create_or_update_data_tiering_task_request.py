# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protection_group_alerting_policy
import cohesity_management_sdk.models_v2.data_tiering_source
import cohesity_management_sdk.models_v2.data_tiering_target
import cohesity_management_sdk.models_v2.data_tiering_schedule
import cohesity_management_sdk.models_v2.downtiering_policy
import cohesity_management_sdk.models_v2.uptiering_policy

class CreateOrUpdateDataTieringTaskRequest(object):

    """Implementation of the 'Create Or Update data tiering task Request.' model.

    Specifies the request to create or update a data tiering task.

    Attributes:
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
        downtiering_policy (DowntieringPolicy): Specifies the data downtiering
            policy.
        uptiering_policy (UptieringPolicy): Specifies the data uptiering
            policy.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "mtype":'type',
        "description":'description',
        "alert_policy":'alertPolicy',
        "source":'source',
        "target":'target',
        "schedule":'schedule',
        "downtiering_policy":'downtieringPolicy',
        "uptiering_policy":'uptieringPolicy'
    }

    def __init__(self,
                 name=None,
                 mtype=None,
                 description=None,
                 alert_policy=None,
                 source=None,
                 target=None,
                 schedule=None,
                 downtiering_policy=None,
                 uptiering_policy=None):
        """Constructor for the CreateOrUpdateDataTieringTaskRequest class"""

        # Initialize members of the class
        self.name = name
        self.description = description
        self.alert_policy = alert_policy
        self.source = source
        self.target = target
        self.schedule = schedule
        self.mtype = mtype
        self.downtiering_policy = downtiering_policy
        self.uptiering_policy = uptiering_policy


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
        description = dictionary.get('description')
        alert_policy = cohesity_management_sdk.models_v2.protection_group_alerting_policy.ProtectionGroupAlertingPolicy.from_dictionary(dictionary.get('alertPolicy')) if dictionary.get('alertPolicy') else None
        source = cohesity_management_sdk.models_v2.data_tiering_source.DataTieringSource.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None
        target = cohesity_management_sdk.models_v2.data_tiering_target.DataTieringTarget.from_dictionary(dictionary.get('target')) if dictionary.get('target') else None
        schedule = cohesity_management_sdk.models_v2.data_tiering_schedule.DataTieringSchedule.from_dictionary(dictionary.get('schedule')) if dictionary.get('schedule') else None
        downtiering_policy = cohesity_management_sdk.models_v2.downtiering_policy.DowntieringPolicy.from_dictionary(dictionary.get('downtieringPolicy')) if dictionary.get('downtieringPolicy') else None
        uptiering_policy = cohesity_management_sdk.models_v2.uptiering_policy.UptieringPolicy.from_dictionary(dictionary.get('uptieringPolicy')) if dictionary.get('uptieringPolicy') else None

        # Return an object of this model
        return cls(name,
                   mtype,
                   description,
                   alert_policy,
                   source,
                   target,
                   schedule,
                   downtiering_policy,
                   uptiering_policy)


