# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_cassandra_snapshot_params
import cohesity_management_sdk.models_v2.key_value_pair

class RecoverCassandraParams(object):

    """Implementation of the 'Recover Cassandra params.' model.

    Specifies the parameters to recover Cassandra objects.

    Attributes:
        advanced_configs (list of KeyValuePair): Specifies the advanced configuration for a recovery job.
        is_live_table_restore (bool): Specifies whether the current recovery operation is a live
            table restore operation.
        is_system_keyspace_restore (bool): Specifies whether the current recovery operation is a system
            keyspace restore operation.
        snapshots (list of RecoverCassandraSnapshotParams): Specifies the
            local snapshot ids and other details of the Objects to be
            recovered.
        recover_to (long|int): Specifies the 'Source Registration ID' of the
            source where the objects are to be recovered. If this is not
            specified, the recovery job will recover to the original
            location.
        overwrite (bool): Set to true to overwrite an existing object at the
            destination. If set to false, and the same object exists at the
            destination, then recovery will fail for that object.
        concurrency (int): Specifies the maximum number of concurrent IO
            Streams that will be created to exchange data with the cluster.
        bandwidth_mbps (long|int): Specifies the maximum network bandwidth
            that each concurrent IO Stream can use for exchanging data with
            the cluster.
        warnings (list of string): This field will hold the warnings in cases
            where the job status is SucceededWithWarnings.
        suffix (string): A suffix that is to be applied to all recovered
            objects.
        selected_data_centers (list of string): Selected Data centers for this
            cluster.
        staging_directory_list (list of string): Specifies the directory on
            the primary to copy the files which are to be uploaded using
            destination sstableloader.
        log_restore_directory (string): Specifies the directory for restoring
            the logs.
        restart_services_task_id (long|int): Specifies the Id of the task required to restart Cassandra
            services.
        restart_services (bool): Specifies whether to restart Cassandra services after the point
            in time recovery.
        restart_immediately (bool): Specifies whether to restart Cassandra services immediately
            after the point in time recovery.
        restart_command (string): Specifies the command to restart Cassandra services after the
            point in time recover
        restart_at_usecs (long|int): Specifies the time in Unix epoch timestamp in microseconds
            at which the Cassandra services are to be restarted.
        recover_privileges (bool): Specifies whether recover/skip roles and permissions.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "advanced_configs":'advancedConfigs',
        "is_live_table_restore":'isLiveTableRestore',
        "is_system_keyspace_restore":'isSystemKeyspaceRestore',
        "snapshots":'snapshots',
        "recover_to":'recoverTo',
        "overwrite":'overwrite',
        "concurrency":'concurrency',
        "bandwidth_mbps":'bandwidthMBPS',
        "warnings":'warnings',
        "suffix":'suffix',
        "selected_data_centers":'selectedDataCenters',
        "staging_directory_list":'stagingDirectoryList',
        "log_restore_directory":'logRestoreDirectory',
        "restart_services_task_id":'restartServicesTaskId',
        "restart_services":'restartServices',
        "restart_immediately":'restartImmediately',
        "restart_command":'restartCommand',
        "restart_at_usecs":'restartAtUsecs',
        "recover_privileges":'recoverPrivileges'
    }

    def __init__(self,
                 advanced_configs=None,
                 is_live_table_restore=None,
                 is_system_keyspace_restore=None,
                 snapshots=None,
                 recover_to=None,
                 overwrite=None,
                 concurrency=None,
                 bandwidth_mbps=None,
                 warnings=None,
                 suffix=None,
                 selected_data_centers=None,
                 staging_directory_list=None,
                 log_restore_directory=None,
                 restart_services_task_id=None,
                 restart_services=None,
                 restart_immediately=None,
                 restart_command=None,
                 restart_at_usecs=None,
                 recover_privileges=None):
        """Constructor for the RecoverCassandraParams class"""

        # Initialize members of the class
        self.advanced_configs = advanced_configs
        self.is_live_table_restore = is_live_table_restore
        self.is_system_keyspace_restore = is_system_keyspace_restore
        self.snapshots = snapshots
        self.recover_to = recover_to
        self.overwrite = overwrite
        self.concurrency = concurrency
        self.bandwidth_mbps = bandwidth_mbps
        self.warnings = warnings
        self.suffix = suffix
        self.selected_data_centers = selected_data_centers
        self.staging_directory_list = staging_directory_list
        self.log_restore_directory = log_restore_directory
        self.restart_services_task_id = restart_services_task_id
        self.restart_services = restart_services
        self.restart_immediately = restart_immediately
        self.restart_command = restart_command
        self.restart_at_usecs = restart_at_usecs
        self.recover_privileges = recover_privileges


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
        advanced_configs = None
        if dictionary.get('advancedConfigs') is not None:
            advanced_configs = list()
            for structure in dictionary.get('advancedConfigs'):
                advanced_configs.append(cohesity_management_sdk.models_v2.key_value_pair.KeyValuePair.from_dictionary(structure))
        is_live_table_restore = dictionary.get('isLiveTableRestore')
        is_system_keyspace_restore = dictionary.get('isSystemKeyspaceRestore')
        snapshots = None
        if dictionary.get("snapshots") is not None:
            snapshots = list()
            for structure in dictionary.get('snapshots'):
                snapshots.append(cohesity_management_sdk.models_v2.recover_cassandra_snapshot_params.RecoverCassandraSnapshotParams.from_dictionary(structure))
        recover_to = dictionary.get('recoverTo')
        overwrite = dictionary.get('overwrite')
        concurrency = dictionary.get('concurrency')
        bandwidth_mbps = dictionary.get('bandwidthMBPS')
        warnings = dictionary.get('warnings')
        suffix = dictionary.get('suffix')
        selected_data_centers = dictionary.get('selectedDataCenters')
        staging_directory_list = dictionary.get('stagingDirectoryList')
        log_restore_directory = dictionary.get('logRestoreDirectory')
        restart_services_task_id = dictionary.get('restartServicesTaskId')
        restart_services = dictionary.get('restartServices')
        restart_immediately = dictionary.get('restartImmediately')
        restart_command = dictionary.get('restartCommand')
        restart_at_usecs = dictionary.get('restartAtUsecs')
        recover_privileges = dictionary.get('recoverPrivileges')

        # Return an object of this model
        return cls(advanced_configs,
                   is_live_table_restore,
                   is_system_keyspace_restore,
                   snapshots,
                   recover_to,
                   overwrite,
                   concurrency,
                   bandwidth_mbps,
                   warnings,
                   suffix,
                   selected_data_centers,
                   staging_directory_list,
                   log_restore_directory,
                   restart_services_task_id,
                   restart_services,
                   restart_immediately,
                   restart_command,
                   restart_at_usecs,
                   recover_privileges)