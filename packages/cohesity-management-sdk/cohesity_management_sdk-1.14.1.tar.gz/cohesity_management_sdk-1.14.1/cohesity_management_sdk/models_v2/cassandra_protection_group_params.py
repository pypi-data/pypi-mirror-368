# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.no_sql_protection_group_object_params

class CassandraProtectionGroupParams(object):

    """Implementation of the 'CassandraProtectionGroupParams' model.

    Specifies the parameters for Cassandra Protection Group.

    Attributes:
        auto_scale_concurrency (bool): Specifies the flag to automatically scale number of concurrent
          IO Streams that will be created to exchange data with the cluster.
        objects (list of NoSqlProtectionGroupObjectParams): Specifies the
            objects to be included in the Protection Group.
        concurrency (int): Specifies the maximum number of concurrent IO
            Streams that will be created to exchange data with the cluster.
        custom_source_name (long|int): The user specified name for the Source on which this protection
          was run.
        bandwidth_mbps (long|int): Specifies the maximum network bandwidth
            that each concurrent IO Stream can use for exchanging data with
            the cluster.
        exclude_object_ids (list of long|int): Specifies the objects to be
            excluded in the Protection Group.
        source_id (long|int): Object ID of the Source on which this protection
            was run .
        source_name (string): Specifies the name of the Source on which this
            protection was run.
        data_centers (list of string): Only the specified data centers will be
            considered while taking backup. The keyspaces having replication
            strategy 'Simple' can be backed up only if all the datacenters for
            the cassandra cluster are specified. For any keyspace having
            replication strategy as 'Network', all the associated data centers
            should be specified.
        is_log_backup (bool): Specifies the type of job for Cassandra. If true,
            only log backup job will be scheduled for the source. This requires
            a policy with log Backup option enabled.
        is_system_keyspace_backup (bool): Specifies whether this ia a system keyspace backup job.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "auto_scale_concurrency":'autoScaleConcurrency',
        "objects":'objects',
        "concurrency":'concurrency',
        "custom_source_name":'customSourceName',
        "bandwidth_mbps":'bandwidthMBPS',
        "exclude_object_ids":'excludeObjectIds',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "data_centers":'dataCenters',
        "is_log_backup":'isLogBackup',
        "is_system_keyspace_backup":'isSystemKeyspaceBackup'
    }

    def __init__(self,
                 auto_scale_concurrency=None,
                 objects=None,
                 concurrency=None,
                 custom_source_name=None,
                 bandwidth_mbps=None,
                 exclude_object_ids=None,
                 source_id=None,
                 source_name=None,
                 data_centers=None,
                 is_log_backup=None,
                 is_system_keyspace_backup=None):
        """Constructor for the CassandraProtectionGroupParams class"""

        # Initialize members of the class
        self.auto_scale_concurrency = auto_scale_concurrency
        self.objects = objects
        self.concurrency = concurrency
        self.custom_source_name = custom_source_name
        self.bandwidth_mbps = bandwidth_mbps
        self.exclude_object_ids = exclude_object_ids
        self.source_id = source_id
        self.source_name = source_name
        self.data_centers = data_centers
        self.is_log_backup = is_log_backup
        self.is_system_keyspace_backup = is_system_keyspace_backup


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
        auto_scale_concurrency = dictionary.get('autoScaleConcurrency')
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.no_sql_protection_group_object_params.NoSqlProtectionGroupObjectParams.from_dictionary(structure))
        concurrency = dictionary.get('concurrency')
        custom_source_name = dictionary.get('customSourceName')
        bandwidth_mbps = dictionary.get('bandwidthMBPS')
        exclude_object_ids = dictionary.get('excludeObjectIds')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        data_centers = dictionary.get('dataCenters')
        is_log_backup = dictionary.get('isLogBackup')
        is_system_keyspace_backup = dictionary.get('isSystemKeyspaceBackup')

        # Return an object of this model
        return cls(auto_scale_concurrency,
                   objects,
                   concurrency,
                   custom_source_name,
                   bandwidth_mbps,
                   exclude_object_ids,
                   source_id,
                   source_name,
                   data_centers,
                   is_log_backup,
                   is_system_keyspace_backup)