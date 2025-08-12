# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.local_snapshot_statistics
import cohesity_management_sdk.models_v2.data_lock_constraints
import cohesity_management_sdk.models_v2.pause_metadata

class SummaryInformationForLocalSnapshotRun(object):

    """Implementation of the 'Summary information for local snapshot run.' model.

    Specifies summary information about local snapshot run across all
    objects.

    Attributes:
        run_type (RunTypeEnum): Type of Protection Group run. 'kRegular'
            indicates an incremental (CBT) backup. Incremental backups
            utilizing CBT (if supported) are captured of the target protection
            objects. The first run of a kRegular schedule captures all the
            blocks. 'kFull' indicates a full (no CBT) backup. A complete
            backup (all blocks) of the target protection objects are always
            captured and Change Block Tracking (CBT) is not utilized. 'kLog'
            indicates a Database Log backup. Capture the database transaction
            logs to allow rolling back to a specific point in time. 'kSystem'
            indicates system volume backup. It produces an image for bare
            metal recovery.
        is_sla_violated (bool): Indicated if SLA has been violated for this
            run.
        start_time_usecs (long|int): Specifies the start time of backup run in
            Unix epoch Timestamp(in microseconds).
        end_time_usecs (long|int): Specifies the end time of backup run in
            Unix epoch Timestamp(in microseconds).
        skipped_objects_count (long|int): Specifies the count of objects for which backup was skipped.
        stats_task_id (string): Stats task id for local backup run.
        status (Status5Enum): Status of the backup run. 'Running' indicates
            that the run is still running. 'Canceled' indicates that the run
            has been canceled. 'Canceling' indicates that the run is in the
            process of being canceled. 'Failed' indicates that the run has
            failed. 'Missed' indicates that the run was unable to take place
            at the scheduled time because the previous run was still
            happening. 'Succeeded' indicates that the run has finished
            successfully. 'SucceededWithWarning' indicates that the run
            finished successfully, but there were some warning messages.
        messages (list of string): Message about the backup run.
        pause_metadata (PauseMetadata): Specifies more information about pause operation.
        successful_objects_count (long|int): Specifies the count of objects
            for which backup was successful.
        failed_objects_count (long|int): Specifies the count of objects for
            which backup failed.
        cancelled_objects_count (long|int): Specifies the count of objects for
            which backup was cancelled.
        successful_app_objects_count (int): Specifies the count of app objects
            for which backup was successful.
        failed_app_objects_count (int): Specifies the count of app objects for
            which backup failed.
        cancelled_app_objects_count (int): Specifies the count of app objects
            for which backup was cancelled.
        local_snapshot_stats (LocalSnapshotStatistics): Specifies statistics
            about local snapshot.
        indexing_task_id (string): Progress monitor task for indexing.
        progress_task_id (string): Progress monitor task id for local backup
            run.
        data_lock (DataLockEnum): This field is deprecated. Use
            DataLockConstraints field instead.
        local_task_id (string): Task ID for a local protection run.
        data_lock_constraints (DataLockConstraints): Specifies the dataLock
            constraints for local or target snapshot.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "run_type":'runType',
        "is_sla_violated":'isSlaViolated',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "skipped_objects_count":'skippedObjectsCount',
        "stats_task_id":'statsTaskId',
        "status":'status',
        "messages":'messages',
        "pause_metadata":'pauseMetadata',
        "successful_objects_count":'successfulObjectsCount',
        "failed_objects_count":'failedObjectsCount',
        "cancelled_objects_count":'cancelledObjectsCount',
        "successful_app_objects_count":'successfulAppObjectsCount',
        "failed_app_objects_count":'failedAppObjectsCount',
        "cancelled_app_objects_count":'cancelledAppObjectsCount',
        "local_snapshot_stats":'localSnapshotStats',
        "indexing_task_id":'indexingTaskId',
        "progress_task_id":'progressTaskId',
        "data_lock":'dataLock',
        "local_task_id":'localTaskId',
        "data_lock_constraints":'dataLockConstraints'
    }

    def __init__(self,
                 run_type=None,
                 is_sla_violated=None,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 skipped_objects_count=None,
                 stats_task_id=None,
                 status=None,
                 messages=None,
                 pause_metadata=None,
                 successful_objects_count=None,
                 failed_objects_count=None,
                 cancelled_objects_count=None,
                 successful_app_objects_count=None,
                 failed_app_objects_count=None,
                 cancelled_app_objects_count=None,
                 local_snapshot_stats=None,
                 indexing_task_id=None,
                 progress_task_id=None,
                 data_lock=None,
                 local_task_id=None,
                 data_lock_constraints=None):
        """Constructor for the SummaryInformationForLocalSnapshotRun class"""

        # Initialize members of the class
        self.run_type = run_type
        self.is_sla_violated = is_sla_violated
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.skipped_objects_count = skipped_objects_count
        self.stats_task_id = stats_task_id
        self.status = status
        self.messages = messages
        self.pause_metadata = pause_metadata
        self.successful_objects_count = successful_objects_count
        self.failed_objects_count = failed_objects_count
        self.cancelled_objects_count = cancelled_objects_count
        self.successful_app_objects_count = successful_app_objects_count
        self.failed_app_objects_count = failed_app_objects_count
        self.cancelled_app_objects_count = cancelled_app_objects_count
        self.local_snapshot_stats = local_snapshot_stats
        self.indexing_task_id = indexing_task_id
        self.progress_task_id = progress_task_id
        self.data_lock = data_lock
        self.local_task_id = local_task_id
        self.data_lock_constraints = data_lock_constraints


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
        run_type = dictionary.get('runType')
        is_sla_violated = dictionary.get('isSlaViolated')
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')
        skipped_objects_count = dictionary.get('skippedObjectsCount')
        stats_task_id = dictionary.get('statsTaskId')
        status = dictionary.get('status')
        messages = dictionary.get('messages')
        pause_metadata = cohesity_management_sdk.models_v2.pause_metadata.PauseMetadata.from_dictionary(dictionary.get('pauseMetadata'))
        successful_objects_count = dictionary.get('successfulObjectsCount')
        failed_objects_count = dictionary.get('failedObjectsCount')
        cancelled_objects_count = dictionary.get('cancelledObjectsCount')
        successful_app_objects_count = dictionary.get('successfulAppObjectsCount')
        failed_app_objects_count = dictionary.get('failedAppObjectsCount')
        cancelled_app_objects_count = dictionary.get('cancelledAppObjectsCount')
        local_snapshot_stats = cohesity_management_sdk.models_v2.local_snapshot_statistics.LocalSnapshotStatistics.from_dictionary(dictionary.get('localSnapshotStats')) if dictionary.get('localSnapshotStats') else None
        indexing_task_id = dictionary.get('indexingTaskId')
        progress_task_id = dictionary.get('progressTaskId')
        data_lock = dictionary.get('dataLock')
        local_task_id = dictionary.get('localTaskId')
        data_lock_constraints = cohesity_management_sdk.models_v2.data_lock_constraints.DataLockConstraints.from_dictionary(dictionary.get('dataLockConstraints')) if dictionary.get('dataLockConstraints') else None

        # Return an object of this model
        return cls(run_type,
                   is_sla_violated,
                   start_time_usecs,
                   end_time_usecs,
                   skipped_objects_count,
                   stats_task_id,
                   status,
                   messages,
                   pause_metadata,
                   successful_objects_count,
                   failed_objects_count,
                   cancelled_objects_count,
                   successful_app_objects_count,
                   failed_app_objects_count,
                   cancelled_app_objects_count,
                   local_snapshot_stats,
                   indexing_task_id,
                   progress_task_id,
                   data_lock,
                   local_task_id,
                   data_lock_constraints)