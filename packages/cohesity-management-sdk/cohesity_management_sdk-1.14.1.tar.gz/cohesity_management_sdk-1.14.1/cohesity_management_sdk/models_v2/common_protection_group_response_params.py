# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.time_of_day
import cohesity_management_sdk.models_v2.protection_group_alerting_policy
import cohesity_management_sdk.models_v2.sla_rule
import cohesity_management_sdk.models_v2.common_protection_group_run_response_parameters
import cohesity_management_sdk.models_v2.tenant
import cohesity_management_sdk.models_v2.missing_entity_params
import cohesity_management_sdk.models_v2.key_value_pair
import cohesity_management_sdk.models_v2.pause_metadata

class CommonProtectionGroupResponseParams(object):

    """Implementation of the 'CommonProtectionGroupResponseParams' model.

    Specifies the parameters which are common between all Protection Group
    responses.

    Attributes:
        id (string): Specifies the ID of the Protection Group.
        invalid_entities (list of MissingEntityParams): Specifies the Information about invalid entities. An entity will
          be considered invalid if it is part of an active protection group but has
          lost compatibility for the given backup type.
        name (string): Specifies the name of the Protection Group.
        num_protected_objects (long|int): Specifies the number of protected objects of the Protection Group.
        pause_in_blackouts (bool): Specifies whether currently executing jobs should be paused if
          a blackout period specified by a policy starts. Available only if the selected
          policy has at least one blackout period. Default value is false. This field
          should not be set to true if 'abortInBlackouts' is sent as true.
        pause_metadata (PauseMetadata): Specifies more information about pause operation.
        policy_id (string): Specifies the unique id of the Protection Policy
            associated with the Protection Group. The Policy provides retry
            settings Protection Schedules, Priority, SLA, etc.
        priority (PriorityEnum): Specifies the priority of the Protection
            Group.
        storage_domain_id (long|int): Specifies the Storage Domain (View Box)
            ID where this Protection Group writes data.
        description (string): Specifies a description of the Protection
            Group.
        start_time (TimeOfDay): Specifies the time of day. Used for scheduling
            purposes.
        end_time_usecs (long|int): Specifies the end time in micro seconds for
            this Protection Group. If this is not specified, the Protection
            Group won't be ended.
        last_modified_timestamp_usecs (long|int): Specifies the last time this
            protection group was updated. If this is passed into a PUT request,
            then the backend will validate that the timestamp passed in matches
            the time that the protection group was actually last modified. If
            the two timestamps do not match, then the request will be rejected
            with a stale error.
        alert_policy (ProtectionGroupAlertingPolicy): Specifies a policy for
            alerting users of the status of a Protection Group.
        cluster_id (string): Specifies the cluster ID.
        region_id (string): Specifies the region ID.
        sla (list of SlaRule): Specifies the SLA parameters for this
            Protection Group.
        qos_policy (QosPolicy1Enum): Specifies whether the Protection Group
            will be written to HDD or SSD.
        abort_in_blackouts (bool): Specifies whether currently executing jobs
            should abort if a blackout period specified by a policy starts.
            Available only if the selected policy has at least one blackout
            period. Default value is false.
        advanced_configs (list of KeyValuePair): Specifies the advanced configuration for a protection job.
        is_active (bool): Specifies if the Protection Group is active or not.
        is_deleted (bool): Specifies if the Protection Group has been
            deleted.
        is_paused (bool): Specifies if the the Protection Group is paused. New
            runs are not scheduled for the paused Protection Groups. Active
            run if any is not impacted.
        environment (Environment7Enum): Specifies the environment of the
            Protection Group.
        last_run (CommonProtectionGroupRunResponseParameters): Protection
            run.
        permissions (list of Tenant): Specifies the list of tenants that have
            permissions for this protection group.
        is_protect_once (bool): Specifies if the the Protection Group is using
            a protect once type of policy. This field is helpful to identify
            run happen for this group.
        missing_entities (list of MissingEntityParams): Specifies the
            Information about missing entities.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "invalid_entities":'invalidEntities',
        "name":'name',
        "num_protected_objects":'numProtectedObjects',
        "pause_in_blackouts":'pauseInBlackouts',
        "pause_metadata":'pauseMetadata',
        "policy_id":'policyId',
        "priority":'priority',
        "storage_domain_id":'storageDomainId',
        "description":'description',
        "start_time":'startTime',
        "end_time_usecs":'endTimeUsecs',
        "last_modified_timestamp_usecs":'lastModifiedTimestampUsecs',
        "alert_policy":'alertPolicy',
        "cluster_id":'clusterId',
        "region_id":'regionId',
        "sla":'sla',
        "qos_policy":'qosPolicy',
        "abort_in_blackouts":'abortInBlackouts',
        "advanced_configs":'advancedConfigs',
        "is_active":'isActive',
        "is_deleted":'isDeleted',
        "is_paused":'isPaused',
        "environment":'environment',
        "last_run":'lastRun',
        "permissions":'permissions',
        "is_protect_once":'isProtectOnce',
        "missing_entities":'missingEntities'
    }

    def __init__(self,
                 id=None,
                 invalid_entities=None,
                 name=None,
                 num_protected_objects=None,
                 pause_in_blackouts=None,
                 pause_metadata=None,
                 policy_id=None,
                 priority=None,
                 storage_domain_id=None,
                 description=None,
                 start_time=None,
                 end_time_usecs=None,
                 last_modified_timestamp_usecs=None,
                 alert_policy=None,
                 cluster_id=None,
                 region_id=None,
                 sla=None,
                 qos_policy=None,
                 abort_in_blackouts=None,
                 advanced_configs=None,
                 is_active=None,
                 is_deleted=None,
                 is_paused=None,
                 environment=None,
                 last_run=None,
                 permissions=None,
                 is_protect_once=None,
                 missing_entities=None):
        """Constructor for the CommonProtectionGroupResponseParams class"""

        # Initialize members of the class
        self.id = id
        self.invalid_entities = invalid_entities
        self.name = name
        self.num_protected_objects = num_protected_objects
        self.pause_in_blackouts = pause_in_blackouts
        self.pause_metadata = pause_metadata
        self.policy_id = policy_id
        self.priority = priority
        self.storage_domain_id = storage_domain_id
        self.description = description
        self.start_time = start_time
        self.end_time_usecs = end_time_usecs
        self.last_modified_timestamp_usecs = last_modified_timestamp_usecs
        self.alert_policy = alert_policy
        self.cluster_id = cluster_id
        self.region_id = region_id
        self.sla = sla
        self.qos_policy = qos_policy
        self.abort_in_blackouts = abort_in_blackouts
        self.advanced_configs = advanced_configs
        self.is_active = is_active
        self.is_deleted = is_deleted
        self.is_paused = is_paused
        self.environment = environment
        self.last_run = last_run
        self.permissions = permissions
        self.is_protect_once = is_protect_once
        self.missing_entities = missing_entities


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
        invalid_entities = None
        if dictionary.get("invalidEntities") is not None :
            invalid_entities = list()
            for structure in dictionary.get('invalidEntities') :
                invalid_entities.append(
                    cohesity_management_sdk.models_v2.missing_entity_params.MissingEntityParams.from_dictionary(
                        structure))
        name = dictionary.get('name')
        num_protected_objects = dictionary.get('numProtectedObjects')
        pause_in_blackouts = dictionary.get('pauseInBlackouts')
        pause_metadata = cohesity_management_sdk.models_v2.pause_metadata.PauseMetadata.from_dictionary(dictionary.get('pauseMetadata')) if dictionary.get('pauseMetadata') else None
        policy_id = dictionary.get('policyId')
        priority = dictionary.get('priority')
        storage_domain_id = dictionary.get('storageDomainId')
        description = dictionary.get('description')
        start_time = cohesity_management_sdk.models_v2.time_of_day.TimeOfDay.from_dictionary(dictionary.get('startTime')) if dictionary.get('startTime') else None
        end_time_usecs = dictionary.get('endTimeUsecs')
        last_modified_timestamp_usecs = dictionary.get('lastModifiedTimestampUsecs')
        alert_policy = cohesity_management_sdk.models_v2.protection_group_alerting_policy.ProtectionGroupAlertingPolicy.from_dictionary(dictionary.get('alertPolicy')) if dictionary.get('alertPolicy') else None
        cluster_id = dictionary.get('clusterId')
        region_id = dictionary.get('regionId')
        sla = None
        if dictionary.get("sla") is not None:
            sla = list()
            for structure in dictionary.get('sla'):
                sla.append(cohesity_management_sdk.models_v2.sla_rule.SlaRule.from_dictionary(structure))
        qos_policy = dictionary.get('qosPolicy')
        abort_in_blackouts = dictionary.get('abortInBlackouts')
        advanced_configs = None
        if dictionary.get('advancedConfigs') is not None:
            advanced_configs = list()
            for structure in dictionary.get('advancedConfigs'):
                advanced_configs.append(cohesity_management_sdk.models_v2.key_value_pair.KeyValuePair.from_dictionary(structure))
        is_active = dictionary.get('isActive')
        is_deleted = dictionary.get('isDeleted')
        is_paused = dictionary.get('isPaused')
        environment = dictionary.get('environment')
        last_run = cohesity_management_sdk.models_v2.common_protection_group_run_response_parameters.CommonProtectionGroupRunResponseParameters.from_dictionary(dictionary.get('lastRun')) if dictionary.get('lastRun') else None
        permissions = None
        if dictionary.get("permissions") is not None:
            permissions = list()
            for structure in dictionary.get('permissions'):
                permissions.append(cohesity_management_sdk.models_v2.tenant.Tenant.from_dictionary(structure))
        is_protect_once = dictionary.get('isProtectOnce')
        missing_entities = None
        if dictionary.get("missingEntities") is not None:
            missing_entities = list()
            for structure in dictionary.get('missingEntities'):
                missing_entities.append(cohesity_management_sdk.models_v2.missing_entity_params.MissingEntityParams.from_dictionary(structure))

        # Return an object of this model
        return cls(id,
                   invalid_entities,
                   name,
                   num_protected_objects,
                   pause_in_blackouts,
                   pause_metadata,
                   policy_id,
                   priority,
                   storage_domain_id,
                   description,
                   start_time,
                   end_time_usecs,
                   last_modified_timestamp_usecs,
                   alert_policy,
                   cluster_id,
                   region_id,
                   sla,
                   qos_policy,
                   abort_in_blackouts,
                   advanced_configs,
                   is_active,
                   is_deleted,
                   is_paused,
                   environment,
                   last_run,
                   permissions,
                   is_protect_once,
                   missing_entities)