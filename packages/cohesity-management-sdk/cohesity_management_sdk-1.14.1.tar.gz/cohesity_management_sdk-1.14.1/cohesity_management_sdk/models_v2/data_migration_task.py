# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protection_group_alerting_policy
import cohesity_management_sdk.models_v2.data_migration_source
import cohesity_management_sdk.models_v2.data_migration_schedule
import cohesity_management_sdk.models_v2.retention
import cohesity_management_sdk.models_v2.down_tiering_policy
import cohesity_management_sdk.models_v2.up_tiering_policy

class DataMigrationTask(object):

    """Implementation of the 'DataMigrationTask' model.

    Specifies the Data Migration task details.

    Attributes:
        name (string): Specifies the name of the Data Migration task.
        description (string): Specifies a description of the Data Migration
            task.
        alert_policy (ProtectionGroupAlertingPolicy): Specifies a policy for
            alerting users of the status of a Protection Group.
        qos_policy (QosPolicyEnum): Specifies whether the Data Migration task
            will be written to HDD or SSD.
        source (DataMigrationSource): Specifies the objects to be migrated.
        target (DataMigrationSource): Specifies the objects to be migrated.
        schedule (DataMigrationSchedule): Specifies the Data Migration
            schedule.
        retention (Retention): Specifies the retention of a backup.
        down_tiering_policy (DownTieringPolicy): Specifies the Data Migration
            downtiering policy.
        up_tiering_policy (UpTieringPolicy): Specifies the Data Migration
            uptiering policy.
        id (string): Specifies the ID of the Data Migration Task.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "description":'description',
        "alert_policy":'alertPolicy',
        "qos_policy":'qosPolicy',
        "source":'source',
        "target":'target',
        "schedule":'schedule',
        "retention":'retention',
        "down_tiering_policy":'downTieringPolicy',
        "up_tiering_policy":'upTieringPolicy',
        "id":'id'
    }

    def __init__(self,
                 name=None,
                 description=None,
                 alert_policy=None,
                 qos_policy=None,
                 source=None,
                 target=None,
                 schedule=None,
                 retention=None,
                 down_tiering_policy=None,
                 up_tiering_policy=None,
                 id=None):
        """Constructor for the DataMigrationTask class"""

        # Initialize members of the class
        self.name = name
        self.description = description
        self.alert_policy = alert_policy
        self.qos_policy = qos_policy
        self.source = source
        self.target = target
        self.schedule = schedule
        self.retention = retention
        self.down_tiering_policy = down_tiering_policy
        self.up_tiering_policy = up_tiering_policy
        self.id = id


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
        description = dictionary.get('description')
        alert_policy = cohesity_management_sdk.models_v2.protection_group_alerting_policy.ProtectionGroupAlertingPolicy.from_dictionary(dictionary.get('alertPolicy')) if dictionary.get('alertPolicy') else None
        qos_policy = dictionary.get('qosPolicy')
        source = cohesity_management_sdk.models_v2.data_migration_source.DataMigrationSource.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None
        target = cohesity_management_sdk.models_v2.data_migration_source.DataMigrationSource.from_dictionary(dictionary.get('target')) if dictionary.get('target') else None
        schedule = cohesity_management_sdk.models_v2.data_migration_schedule.DataMigrationSchedule.from_dictionary(dictionary.get('schedule')) if dictionary.get('schedule') else None
        retention = cohesity_management_sdk.models_v2.retention.Retention.from_dictionary(dictionary.get('retention')) if dictionary.get('retention') else None
        down_tiering_policy = cohesity_management_sdk.models_v2.down_tiering_policy.DownTieringPolicy.from_dictionary(dictionary.get('downTieringPolicy')) if dictionary.get('downTieringPolicy') else None
        up_tiering_policy = cohesity_management_sdk.models_v2.up_tiering_policy.UpTieringPolicy.from_dictionary(dictionary.get('upTieringPolicy')) if dictionary.get('upTieringPolicy') else None
        id = dictionary.get('id')

        # Return an object of this model
        return cls(name,
                   description,
                   alert_policy,
                   qos_policy,
                   source,
                   target,
                   schedule,
                   retention,
                   down_tiering_policy,
                   up_tiering_policy,
                   id)


