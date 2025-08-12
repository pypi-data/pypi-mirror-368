# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.local_snapshot_statistics
import cohesity_management_sdk.models_v2.data_lock_constraints

class SnapshotInformationForAnObject(object):

    """Implementation of the 'Snapshot information for an object.' model.

    Snapshot info for an object.

    Attributes:
        snapshot_id (string): Snapshot id for a successful snapshot. This
            field will not be set if the Protection Group Run has no
            successful attempt.
        status (Status4Enum): Status of snapshot.
        start_time_usecs (long|int): Specifies the start time of attempt in
            Unix epoch Timestamp(in microseconds) for an object.
        data_lock_constraints (DataLockConstraints):  Specifies the dataLock constraints
            for the snapshot info.
        end_time_usecs (long|int): Specifies the end time of attempt in Unix
            epoch Timestamp(in microseconds) for an object.
        admitted_time_usecs (long|int): Specifies the time at which the backup
            task was admitted to run in Unix epoch Timestamp(in microseconds)
            for an object.
        snapshot_creation_time_usecs (long|int): Specifies the time at which
            the source snapshot was taken in Unix epoch Timestamp(in
            microseconds) for an object.
        stats (LocalSnapshotStatistics): Specifies statistics about local
            snapshot.
        permit_grant_time_usecs (long|int): Specifies the time when gatekeeper permit is granted to the backup
          task. If the backup task is rescheduled due to errors, the field is updated
          to the time when permit is granted again.
        progress_task_id (string): Progress monitor task for an object.
        queue_duration_usecs (long|int): Specifies the duration between the startTime and when gatekeeper
          permit is granted to the backup task. If the backup task is rescheduled
          due to errors, the field is updated considering the time when permit is
          granted again. Queue duration = PermitGrantTimeUsecs - StartTimeUsecs
        warnings (list of string): Specifies a list of warning messages.
        indexing_task_id (string): Progress monitor task for the indexing of documents in an object.
        is_manually_deleted (bool): Specifies whether the snapshot is deleted
            manually.
        expiry_time_usecs (long|int): Specifies the expiry time of attempt in
            Unix epoch Timestamp (in microseconds) for an object.
        stats_task_id (string): Stats task for an object.
        status_message (string): A message decribing the status. This will be populated currently
          only for kWaitingForOlderBackupRun status.
        total_file_count (long|int): The total number of file and directory
            entities visited in this backup. Only applicable to file based
            backups.
        backup_file_count (long|int): The total number of file and directory
            entities that are backed up in this run. Only applicable to file
            based backups.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "snapshot_id":'snapshotId',
        "status":'status',
        "start_time_usecs":'startTimeUsecs',
        "data_lock_constraints":'dataLockConstraints',
        "end_time_usecs":'endTimeUsecs',
        "admitted_time_usecs":'admittedTimeUsecs',
        "snapshot_creation_time_usecs":'snapshotCreationTimeUsecs',
        "stats":'stats',
        "permit_grant_time_usecs":'permitGrantTimeUsecs',
        "progress_task_id":'progressTaskId',
        "queue_duration_usecs":'queueDurationUsecs',
        "warnings":'warnings',
        "stats_task_id":'statsTaskId',
        "indexing_task_id":'indexingTaskId',
        "is_manually_deleted":'isManuallyDeleted',
        "expiry_time_usecs":'expiryTimeUsecs',
        "status_message":'statusMessage',
        "total_file_count":'totalFileCount',
        "backup_file_count":'backupFileCount'
    }

    def __init__(self,
                 snapshot_id=None,
                 status=None,
                 start_time_usecs=None,
                 data_lock_constraints=None,
                 end_time_usecs=None,
                 admitted_time_usecs=None,
                 snapshot_creation_time_usecs=None,
                 stats=None,
                 stats_task_id=None,
                 permit_grant_time_usecs=None,
                 progress_task_id=None,
                 queue_duration_usecs=None,
                 warnings=None,
                 indexing_task_id=None,
                 is_manually_deleted=None,
                 expiry_time_usecs=None,
                 status_message=None,
                 total_file_count=None,
                 backup_file_count=None):
        """Constructor for the SnapshotInformationForAnObject class"""

        # Initialize members of the class
        self.snapshot_id = snapshot_id
        self.status = status
        self.start_time_usecs = start_time_usecs
        self.data_lock_constraints = data_lock_constraints
        self.end_time_usecs = end_time_usecs
        self.admitted_time_usecs = admitted_time_usecs
        self.snapshot_creation_time_usecs = snapshot_creation_time_usecs
        self.stats = stats
        self.stats_task_id = stats_task_id
        self.permit_grant_time_usecs = permit_grant_time_usecs
        self.progress_task_id = progress_task_id
        self.queue_duration_usecs = queue_duration_usecs
        self.warnings = warnings
        self.indexing_task_id = indexing_task_id
        self.is_manually_deleted = is_manually_deleted
        self.expiry_time_usecs = expiry_time_usecs
        self.status_message = status_message
        self.total_file_count = total_file_count
        self.backup_file_count = backup_file_count


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
        snapshot_id = dictionary.get('snapshotId')
        status = dictionary.get('status')
        start_time_usecs = dictionary.get('startTimeUsecs')
        data_lock_constraints = cohesity_management_sdk.models_v2.data_lock_constraints.DataLockConstraints.from_dictionary(dictionary.get('dataLockConstraints')) if dictionary.get('dataLockConstraints') else None
        end_time_usecs = dictionary.get('endTimeUsecs')
        admitted_time_usecs = dictionary.get('admittedTimeUsecs')
        snapshot_creation_time_usecs = dictionary.get('snapshotCreationTimeUsecs')
        stats = cohesity_management_sdk.models_v2.local_snapshot_statistics.LocalSnapshotStatistics.from_dictionary(dictionary.get('stats')) if dictionary.get('stats') else None
        stats_task_id = dictionary.get('statsTaskId')
        permit_grant_time_usecs = dictionary.get('permitGrantTimeUsecs')
        progress_task_id = dictionary.get('progressTaskId')
        queue_duration_usecs = dictionary.get('queueDurationUsecs')
        warnings = dictionary.get('warnings')
        indexing_task_id = dictionary.get('indexingTaskId')
        is_manually_deleted = dictionary.get('isManuallyDeleted')
        expiry_time_usecs = dictionary.get('expiryTimeUsecs')
        status_message = dictionary.get('statusMessage')
        total_file_count = dictionary.get('totalFileCount')
        backup_file_count = dictionary.get('backupFileCount')

        # Return an object of this model
        return cls(snapshot_id,
                   status,
                   start_time_usecs,
                   data_lock_constraints,
                   end_time_usecs,
                   admitted_time_usecs,
                   snapshot_creation_time_usecs,
                   stats,
                   stats_task_id,
                   permit_grant_time_usecs,
                   progress_task_id,
                   queue_duration_usecs,
                   warnings,
                   indexing_task_id,
                   is_manually_deleted,
                   expiry_time_usecs,
                   status_message,
                   total_file_count,
                   backup_file_count)