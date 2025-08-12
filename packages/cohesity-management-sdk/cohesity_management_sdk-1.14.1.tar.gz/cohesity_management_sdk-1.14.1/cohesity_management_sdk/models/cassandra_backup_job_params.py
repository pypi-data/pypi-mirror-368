# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.cassandra_additional_params

class CassandraBackupJobParams(object):

    """Implementation of the 'CassandraBackupJobParams' model.

    Contains any additional cassandra environment specific backup params at
    the
    job level.

    Attributes:
        cassandra_additional_info (CassandraAdditionalParams): Additional
            parameters required for Cassandra backup.
        graph_handling_enabled (bool): whether special graph handling is
            enabled.
        is_only_log_backup_job (bool): If this backup job is only responsible
            for the log backups. Presently this is used for cassandra log
            backups.
        is_system_ks_backup (bool): Whether this is a system keyspace backup
        job_start_time_in_usecs (long|int): Start time of the current job (
            slave start time)
        make_primary_log_backup (bool): Make source primary for log-backup in
            this job run
        previous_job_end_time_in_usecs (long|int): End time of the previous job
            (set in snapshot_info)
        retention_period_in_secs (long|int): Retention period in seconds. This
            is read from the policy currently attached to the protection job.
            This field is used only in case of log backups and ignored for
            other backups.
        roles_gflag_enabled (bool): Whether cassandra roles backup/restore is
            enabled or not.
        selected_data_center_vec (list of string):  The data centers selected
            for backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cassandra_additional_info": 'cassandraAdditionalInfo',
        "graph_handling_enabled":'graphHandlingEnabled',
        "is_only_log_backup_job":'isOnlyLogBackupJob',
        "is_system_ks_backup": 'isSystemKsBackup',
        "job_start_time_in_usecs": 'jobStartTimeInUsecs',
        "make_primary_log_backup": 'makePrimaryLogBackup',
        "previous_job_end_time_in_usecs": 'previousJobEndTimeInUsecs',
        "retention_period_in_secs":'retentionPeriodInSecs',
        "roles_gflag_enabled": 'rolesGflagEnabled',
        "selected_data_center_vec": 'selectedDataCenterVec'
    }

    def __init__(self,
                 cassandra_additional_info=None,
                 graph_handling_enabled=None,
                 is_only_log_backup_job=None,
                 is_system_ks_backup=None,
                 job_start_time_in_usecs=None,
                 make_primary_log_backup=None,
                 previous_job_end_time_in_usecs=None,
                 retention_period_in_secs=None,
                 roles_gflag_enabled=None,
                 selected_data_center_vec=None):
        """Constructor for the CassandraBackupJobParams class"""

        # Initialize members of the class
        self.cassandra_additional_info = cassandra_additional_info
        self.graph_handling_enabled = graph_handling_enabled
        self.is_only_log_backup_job = is_only_log_backup_job
        self.is_system_ks_backup = is_system_ks_backup
        self.job_start_time_in_usecs = job_start_time_in_usecs
        self.make_primary_log_backup = make_primary_log_backup
        self.previous_job_end_time_in_usecs = previous_job_end_time_in_usecs
        self.retention_period_in_secs = retention_period_in_secs
        self.roles_gflag_enabled = roles_gflag_enabled
        self.selected_data_center_vec = selected_data_center_vec


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
        cassandra_additional_info = cohesity_management_sdk.models.cassandra_additional_params.CassandraAdditionalParams.from_dictionary(dictionary.get('cassandraAdditionalInfo')) if dictionary.get('cassandraAdditionalInfo') else None
        graph_handling_enabled = dictionary.get('graphHandlingEnabled')
        is_only_log_backup_job = dictionary.get('isOnlyLogBackupJob')
        is_system_ks_backup = dictionary.get('isSystemKsBackup')
        job_start_time_in_usecs = dictionary.get('jobStartTimeInUsecs')
        make_primary_log_backup = dictionary.get('makePrimaryLogBackup')
        previous_job_end_time_in_usecs = dictionary.get('previousJobEndTimeInUsecs')
        retention_period_in_secs = dictionary.get('retentionPeriodInSecs')
        roles_gflag_enabled = dictionary.get('rolesGflagEnabled')
        selected_data_center_vec = dictionary.get('selectedDataCenterVec', None)

        # Return an object of this model
        return cls(cassandra_additional_info,
                   graph_handling_enabled,
                   is_only_log_backup_job,
                   is_system_ks_backup,
                   job_start_time_in_usecs,
                   make_primary_log_backup,
                   previous_job_end_time_in_usecs,
                   retention_period_in_secs,
                   roles_gflag_enabled,
                   selected_data_center_vec)


