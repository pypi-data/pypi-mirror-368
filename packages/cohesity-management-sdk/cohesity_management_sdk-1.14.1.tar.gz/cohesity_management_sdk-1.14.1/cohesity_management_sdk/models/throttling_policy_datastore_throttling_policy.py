# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.throttling_policy_latency_thresholds
import cohesity_management_sdk.models.throttling_policy_datastore_streams_config
import cohesity_management_sdk.models.entity_proto

class ThrottlingPolicy_DatastoreThrottlingPolicy(object):

    """Implementation of the 'ThrottlingPolicy_DatastoreThrottlingPolicy' model.

    Protobuf that describes the access control list (ACL) permissions for a
    bucket or for an object.

    Attributes:
        latency_thresholds (ThrottlingPolicy_LatencyThresholds):This specifies
            custom latency thresholds for this particular datastore
            that override the global latency thresholds
        datastore_streams_config (ThrottlingPolicy_DatastoreStreamsConfig):
            This specifies custom datastore streams config for this datastore
            that override the global datastore streams config.
        datastore_entity (EntityProto):  The datastore entity that the latency
            thresholds apply to.
        is_throttling_enabled (bool): Whether we will adaptively throttle read
            operations from this datastore.
            This can be used to disable throttling for this particular datastore
            when throttling is enabled at the global level.
            Note: This is only applicable to latency throttling
        is_datastore_streams_config_enabled (bool):If set to true, the max space
            for this volume will be according to datastore_streams_config.
            If set to false, the max space for this volume will be uncapped.
            If not set, there is not max snapshot override for this volume.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "latency_thresholds":'latencyThresholds',
        "datastore_streams_config":'datastoreStreamsConfig',
        "datastore_entity":'datastoreEntity',
        "is_throttling_enabled":'isThrottlingEnabled',
        "is_datastore_streams_config_enabled":'isDatastoreStreamsConfigEnabled'
    }

    def __init__(self,
                 latency_thresholds=None,
                 datastore_streams_config=None,
                 datastore_entity=None,
                 is_throttling_enabled=None,
                 is_datastore_streams_config_enabled=None):
        """Constructor for the ThrottlingPolicy_DatastoreThrottlingPolicy class"""

        # Initialize members of the class
        self.latency_thresholds = latency_thresholds
        self.datastore_streams_config = datastore_streams_config
        self.datastore_entity = datastore_entity
        self.is_throttling_enabled = is_throttling_enabled
        self.is_datastore_streams_config_enabled = is_datastore_streams_config_enabled


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
        latency_thresholds = cohesity_management_sdk.models.throttling_policy_latency_thresholds.ThrottlingPolicy_LatencyThresholds.from_dictionary(dictionary.get('latencyThresholds')) if dictionary.get('latencyThresholds') else None
        datastore_streams_config = cohesity_management_sdk.models.throttling_policy_datastore_streams_config.ThrottlingPolicy_DatastoreStreamsConfig.from_dictionary(dictionary.get('datastoreStreamsConfig')) if dictionary.get('datastoreStreamsConfig') else None
        datastore_entity = cohesity_management_sdk.models.entity_proto.EntityProto.from_dictionary(dictionary.get('datastoreEntity')) if dictionary.get('datastoreEntity') else None
        is_datastore_streams_config_enabled = dictionary.get('isDatastoreStreamsConfigEnabled')
        is_throttling_enabled = dictionary.get('isThrottlingEnabled')

        # Return an object of this model
        return cls(latency_thresholds,
                   datastore_streams_config,
                   datastore_entity,
                   is_throttling_enabled,
                   is_datastore_streams_config_enabled)