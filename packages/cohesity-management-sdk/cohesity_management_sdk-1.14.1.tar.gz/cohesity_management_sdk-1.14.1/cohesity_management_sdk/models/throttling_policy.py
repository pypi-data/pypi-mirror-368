# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.entity_proto
import cohesity_management_sdk.models.throttling_policy_datastore_streams_config
import cohesity_management_sdk.models.throttling_policy_datastore_throttling_policy
import cohesity_management_sdk.models.throttling_policy_latency_thresholds
import cohesity_management_sdk.models.throttling_policy_storage_array_snapshot_max_snapshot_config
import cohesity_management_sdk.models.throttling_policy_registered_source_throttling_config
import cohesity_management_sdk.models.throttling_policy_storage_array_snapshot_max_space_config
import cohesity_management_sdk.models.throttling_policy_storage_array_snapshot_throttling_policy

class ThrottlingPolicy(object):

    """Implementation of the 'ThrottlingPolicy' model.

    Message that specifies the throttling policy for a particular registered
    entity.

    Attributes:
        datastore_streams_config (ThrottlingPolicy_DatastoreStreamsConfig):
            This specifies the datastore streams config applied to all datastores
            that are part of the registered entity. This policy can be overriden per
            datastore by specifying it in DatastoreThrottlingPolicy below.
        datastore_throttling_policies (list of ThrottlingPolicy_DatastoreThrottlingPolicy):
            This field can be used to override the throttling policy for
            individual datastores.
        entity (EntityProto): The registered entity for which this throttling
            policy applies.
            NOTE: This field is optional and need not be set by Iris.
        is_datastore_streams_config_enabled (bool):Whether datastore streams can
            be configured on all datastores that are
            part of the registered entity. If set to true, then the config within
            ''DatastoreStreamsConfig'' would be applicable to all those datastores
        is_max_snapshots_config_enabled (bool): Whether we will use storage
            snapshot managmement max snap config to all
            volumes/luns that are part of the registered entity.
        is_max_space_config_enabled (bool): Whether we will use storage
            snapshot managmement max space config to all
            volumes/luns that are part of the registered entity.
        is_registered_source_throttling_config_enabled (bool): Whether no. of backups
            can be configured on the registered entity. If set
            to true, then the config within ''RegisteredSourceThrottlingConfig'' would
            be applicable to the registered entity
        is_throttling_enabled (long|int): Whether we will adaptively throttle read
            operations from the datastores that are part of the registered entity.
            Note: This is only applicable to latency throttling
        latency_thresholds (ThrottlingPolicy_LatencyThresholds): This specifies the
            thresholds that should be applied to all  datastores
            that are part of the registered entity. The thresholds for a datastore can
            be overriden by specifying it in datastore_throttling_policy below.
        registered_source_throttling_config (ThrottlingPolicy_RegisteredSourceThrottlingConfig): 
            This specifies the registered source throttling config applied
            to registered entity.
        storageArray_snapshot_max_snapshot_config (
            ThrottlingPolicy_StorageArraySnapshotMaxSnapshotConfig): This
            specifies the storage snapshot managmement max snap config applied
            to all volumes/lun that are part of the registered entity. This policy
            can be overriden per volume/lun  by specifying it in
            StorageArraySnapshotThrottlingPolicy below.
        storage_array_snapshot_max_space_config (
            ThrottlingPolicy_StorageArraySnapshotMaxSpaceConfig): This specifies
            the storage snapshot managmement max space config applied
            to all volumes/lun that are part of the registered entity. This policy
            can be overriden per volume/lun  by specifying it in
            StorageArraySnapshotThrottlingPolicy below
        storage_array_snapshot_throttling_policies (list of
            ThrottlingPolicy_StorageArraySnapshotThrottlingPolicy):  This field
            is used for throttling policy for individual volume/lun.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "datastore_streams_config":'datastoreStreamsConfig',
        "datastore_throttling_policies":'datastoreThrottlingPolicies',
        "entity":'entity',
        "is_datastore_streams_config_enabled":'isDatastoreStreamsConfigEnabled',
        "is_max_snapshots_config_enabled": 'isMaxSnapshotsConfigEnabled',
        "is_max_space_config_enabled":'isMaxSpaceConfigEnabled',
        "is_registered_source_throttling_config_enabled":'isRegisteredSourceThrottlingConfigEnabled',
        "is_throttling_enabled":'isThrottlingEnabled',
        "latency_thresholds":'latencyThresholds',
        "registered_source_throttling_config":'registeredSourceThrottlingConfig',
        "storageArray_snapshot_max_snapshot_config":'storageArraySnapshotMaxSnapshotConfig',
        "storage_array_snapshot_max_space_config":'storageArraySnapshotMaxSpaceConfig',
        "storage_array_snapshot_throttling_policies":'storageArraySnapshotThrottlingPolicies'
    }

    def __init__(self,
                 datastore_streams_config=None,
                 datastore_throttling_policies=None,
                 entity=None,
                 is_datastore_streams_config_enabled=None,
                 is_max_snapshots_config_enabled=None,
                 is_max_space_config_enabled=None,
                 is_registered_source_throttling_config_enabled=None,
                 is_throttling_enabled=None,
                 latency_thresholds=None,
                 registered_source_throttling_config=None,
                 storageArray_snapshot_max_snapshot_config=None,
                 storage_array_snapshot_max_space_config=None,
                 storage_array_snapshot_throttling_policies=None):
        """Constructor for the ThrottlingPolicy class"""

        # Initialize members of the class
        self.datastore_streams_config = datastore_streams_config
        self.datastore_throttling_policies = datastore_throttling_policies
        self.entity = entity
        self.is_datastore_streams_config_enabled = is_datastore_streams_config_enabled
        self.is_max_snapshots_config_enabled = is_max_snapshots_config_enabled
        self.is_max_space_config_enabled = is_max_space_config_enabled
        self.is_registered_source_throttling_config_enabled = is_registered_source_throttling_config_enabled
        self.is_throttling_enabled = is_throttling_enabled
        self.latency_thresholds = latency_thresholds
        self.registered_source_throttling_config = registered_source_throttling_config
        self.storageArray_snapshot_max_snapshot_config = storageArray_snapshot_max_snapshot_config
        self.storage_array_snapshot_max_space_config = storage_array_snapshot_max_space_config
        self.storage_array_snapshot_throttling_policies = storage_array_snapshot_throttling_policies


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
        datastore_streams_config = cohesity_management_sdk.models.throttling_policy_datastore_streams_config.ThrottlingPolicy_DatastoreStreamsConfig.from_dictionary(dictionary.get('datastoreStreamsConfig')) if dictionary.get('datastoreStreamsConfig') else None
        datastore_throttling_policies = None
        if dictionary.get("datastoreThrottlingPolicies") is not None:
            datastore_throttling_policies = list()
            for structure in dictionary.get('datastoreThrottlingPolicies'):
                datastore_throttling_policies.append(cohesity_management_sdk.models.throttling_policy_datastore_throttling_policy.ThrottlingPolicy_DatastoreThrottlingPolicy.from_dictionary(structure))
        entity = cohesity_management_sdk.models.entity_proto.EntityProto.from_dictionary(dictionary.get('entity')) if dictionary.get('entity') else None
        is_datastore_streams_config_enabled = dictionary.get('isDatastoreStreamsConfigEnabled')
        is_max_snapshots_config_enabled = dictionary.get('isMaxSnapshotsConfigEnabled')
        is_max_space_config_enabled = dictionary.get('isMaxSpaceConfigEnabled')
        is_registered_source_throttling_config_enabled = dictionary.get('isRegisteredSourceThrottlingConfigEnabled')
        is_throttling_enabled = dictionary.get('isThrottlingEnabled')
        latency_thresholds = cohesity_management_sdk.models.throttling_policy_latency_thresholds.ThrottlingPolicy_LatencyThresholds.from_dictionary(dictionary.get('latencyThresholds')) if dictionary.get('latencyThresholds') else None
        registered_source_throttling_config = cohesity_management_sdk.models.throttling_policy_storage_array_snapshot_max_snapshot_config.ThrottlingPolicy_RegisteredSourceThrottlingConfig.from_dictionary(dictionary.get('registeredSourceThrottlingConfig')) if dictionary.get('registeredSourceThrottlingConfig') else None
        storageArray_snapshot_max_snapshot_config = cohesity_management_sdk.models.throttling_policy_registered_source_throttling_config.ThrottlingPolicy_StorageArraySnapshotMaxSnapshotConfig.from_dictionary(dictionary.get('storageArraySnapshotMaxSnapshotConfig')) if dictionary.get('storageArraySnapshotMaxSnapshotConfig') else None
        storage_array_snapshot_max_space_config = cohesity_management_sdk.models.throttling_policy_storage_array_snapshot_max_space_config.ThrottlingPolicy_StorageArraySnapshotMaxSpaceConfig.from_dictionary(dictionary.get('storageArraySnapshotMaxSpaceConfig')) if dictionary.get('storageArraySnapshotMaxSpaceConfig') else None
        storage_array_snapshot_throttling_policies = None
        if dictionary.get("storageArraySnapshotThrottlingPolicies") is not None:
            storage_array_snapshot_throttling_policies = list()
            for structure in dictionary.get('storageArraySnapshotThrottlingPolicies'):
                storage_array_snapshot_throttling_policies.append(cohesity_management_sdk.models.throttling_policy_storage_array_snapshot_throttling_policy.ThrottlingPolicy_StorageArraySnapshotThrottlingPolicy.from_dictionary(structure))

        # Return an object of this model
        return cls(datastore_streams_config,
                   datastore_throttling_policies,
                   entity,
                   is_datastore_streams_config_enabled,
                   is_max_snapshots_config_enabled,
                   is_max_space_config_enabled,
                   is_registered_source_throttling_config_enabled,
                   is_throttling_enabled,
                   latency_thresholds,
                   registered_source_throttling_config,
                   storageArray_snapshot_max_snapshot_config,
                   storage_array_snapshot_max_space_config,
                   storage_array_snapshot_throttling_policies)


