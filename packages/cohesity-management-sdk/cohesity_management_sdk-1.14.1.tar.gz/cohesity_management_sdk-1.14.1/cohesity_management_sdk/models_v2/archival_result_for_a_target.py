# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.archival_data_statistics
import cohesity_management_sdk.models_v2.data_lock_constraints
import cohesity_management_sdk.models_v2.archival_target_tier_info
import cohesity_management_sdk.models_v2.worm_archival_data

class ArchivalResultForATarget(object):

    """Implementation of the 'Archival result for a target.' model.

    Archival result for an archival target.

    Attributes:
        archival_task_id (string): Specifies the archival task id. This is a
            protection group UID which only applies when archival type is
            'Tape'.
        ownership_context (ownershipContext2Enum): Specifies the ownership context for the target.
        target_id (long|int): Specifies the archival target ID.
        target_name (string): Specifies the archival target name.
        target_type (TargetType1Enum): Specifies the archival target type.
        tier_settings (ArchivalTargetTierInfo): Specifies the tier level settings configured with archival target.
          This will be specified if the run is a CAD run.
        usage_type (UsageTypeEnum): Specifies the usage type for the target.
        cancelled_app_objects_count (long|int): Specifies the count of app objects for which backup was cancelled.
        cancelled_objects_count (long|int): Specifies the count of objects for which backup was cancelled.
        data_lock_constraints (DataLockConstraints): Specifies the dataLock constraints for the archival target.
        end_time_usecs (long|int): Specifies the end time of replication run in Unix epoch Timestamp(in
            microseconds) for an archival target.
        expiry_time_usecs (long|int): Specifies the expiry time of attempt in Unix epoch Timestamp
            (in microseconds).
        failed_app_objects_count (long|int): Specifies the count of app objects for which backup failed.
        failed_objects_count (long|int): Specifies the count of objects for which backup failed.
        indexing_task_id (string): Progress monitor task for indexing.
        is_cad_archive (bool): Whether this is CAD archive or not
        is_forever_incremental (bool): Whether this is forever incremental or not
        is_incremental (bool): Whether this is an incremental archive. If set to true, this
            is an incremental archive, otherwise this is a full archive.
        is_manually_deleted (bool): Specifies whether the snapshot is deleted manually.
        is_sla_violated (bool): Indicated if SLA has been violated for this run.
        message (string): Message about the archival run.
        on_legal_hold (bool): onLegalHold
        progress_task_id (string): Progress monitor task id for archival.
        queued_time_usecs (long|int): Specifies the time when the archival is queued for schedule
            in Unix epoch Timestamp(in microseconds) for a target.
        run_type (runType6Enum): Type of Protection Group run. 'kRegular' indicates an incremental
            (CBT) backup. Incremental backups utilizing CBT (if supported) are captured
            of the target protection objects. The first run of a kRegular schedule
            captures all the blocks. 'kFull' indicates a full (no CBT) backup. A complete
            backup (all blocks) of the target protection objects are always captured
            and Change Block Tracking (CBT) is not utilized. 'kLog' indicates a Database
            Log backup. Capture the database transaction logs to allow rolling back
            to a specific point in time. 'kSystem' indicates system volume backup.
            It produces an image for bare metal recovery.
        snapshot_id (string): Snapshot id for a successful snapshot. This field will not
            be set if the archival Run fails to take the snapshot.
        start_time_usecs (long|int): Specifies the start time of replication run in Unix epoch Timestamp(in
            microseconds) for an archival target.
        stats (ArchivalDataStats): Archival data statistics for a target.
        stats_task_id (string): Run Stats task id for archival.
        status (status9Enum): Status of the replication run for an archival target. 'Running'
            indicates that the run is still running. 'Canceled' indicates that the
            run has been canceled. 'Canceling' indicates that the run is in the process
            of being canceled. 'Paused' indicates that the ongoing run has been paused.
            'Failed' indicates that the run has failed. 'Missed' indicates that the
            run was unable to take place at the scheduled time because the previous
            run was still happening. 'Succeeded' indicates that the run has finished
            successfully. 'SucceededWithWarning' indicates that the run finished successfully,
            but there were some warning messages. 'Skipped' indicates that the run
            was skipped.
        successful_objects_count (long|int): Specifies the count of objects for which backup was successful.
        successful_app_objects_count (long|int): Specifies the count of objects for which backup was successful.
        worm_properties (WormProperties): Specifies the worm related properties for this archive.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "archival_task_id":'archivalTaskId',
        "ownership_context":'ownershipContext',
        "target_id":'targetId',
        "target_name":'targetName',
        "target_type":'targetType',
        "tier_settings":'tierSettings',
        "usage_type":'usageType',
        "cancelled_app_objects_count":'cancelledAppObjectsCount',
        "cancelled_objects_count":'cancelledObjectsCount',
        "data_lock_constraints":'dataLockConstraints',
        "end_time_usecs":'endTimeUsecs',
        "expiry_time_usecs":'expiryTimeUsecs',
        "failed_app_objects_count":'failedAppObjectsCount',
        "failed_objects_count":'failedObjectsCount',
        "run_type":'runType',
        "is_sla_violated":'isSlaViolated',
        "snapshot_id":'snapshotId',
        "start_time_usecs":'startTimeUsecs',
        "queued_time_usecs":'queuedTimeUsecs',
        "is_incremental":'isIncremental',
        "is_forever_incremental":'isForeverIncremental',
        "is_cad_archive":'isCadArchive',
        "status":'status',
        "message":'message',
        "progress_task_id":'progressTaskId',
        "stats_task_id":'statsTaskId',
        "indexing_task_id":'indexingTaskId',
        "successful_objects_count":'successfulObjectsCount',
        "successful_app_objects_count":'successfulAppObjectsCount',
        "stats":'stats',
        "is_manually_deleted":'isManuallyDeleted',
        "on_legal_hold":'onLegalHold',
        "worm_properties":'wormProperties'
    }

    def __init__(self,
                 archival_task_id=None,
                 ownership_context=None,
                 target_id=None,
                 target_name=None,
                 target_type=None,
                 tier_settings=None,
                 usage_type=None,
                 cancelled_app_objects_count=None,
                 cancelled_objects_count=None,
                 data_lock_constraints=None,
                 end_time_usecs=None,
                 expiry_time_usecs=None,
                 failed_app_objects_count=None,
                 failed_objects_count=None,
                 run_type=None,
                 is_sla_violated=None,
                 snapshot_id=None,
                 start_time_usecs=None,
                 queued_time_usecs=None,
                 is_incremental=None,
                 is_forever_incremental=None,
                 is_cad_archive=None,
                 status=None,
                 message=None,
                 progress_task_id=None,
                 stats_task_id=None,
                 indexing_task_id=None,
                 successful_objects_count=None,
                 successful_app_objects_count=None,
                 stats=None,
                 is_manually_deleted=None,
                 on_legal_hold=None,
                 worm_properties=None):
        """Constructor for the ArchivalResultForATarget class"""

        # Initialize members of the class
        self.archival_task_id = archival_task_id
        self.ownership_context = ownership_context
        self.target_id = target_id
        self.target_name = target_name
        self.target_type = target_type
        self.tier_settings = tier_settings
        self.usage_type = usage_type
        self.cancelled_app_objects_count = cancelled_app_objects_count
        self.cancelled_objects_count = cancelled_objects_count
        self.data_lock_constraints = data_lock_constraints
        self.end_time_usecs = end_time_usecs
        self.expiry_time_usecs = expiry_time_usecs
        self.failed_app_objects_count = failed_app_objects_count
        self.failed_objects_count = failed_objects_count
        self.run_type = run_type
        self.is_sla_violated = is_sla_violated
        self.snapshot_id = snapshot_id
        self.start_time_usecs = start_time_usecs
        self.queued_time_usecs = queued_time_usecs
        self.is_incremental = is_incremental
        self.is_forever_incremental = is_forever_incremental
        self.is_cad_archive = is_cad_archive
        self.status = status
        self.message = message
        self.progress_task_id = progress_task_id
        self.stats_task_id = stats_task_id
        self.indexing_task_id = indexing_task_id
        self.successful_objects_count = successful_objects_count
        self.successful_app_objects_count = successful_app_objects_count
        self.stats = stats
        self.is_manually_deleted = is_manually_deleted
        self.on_legal_hold = on_legal_hold
        self.worm_properties = worm_properties

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
        archival_task_id = dictionary.get('archivalTaskId')
        ownership_context = dictionary.get('ownershipContext')
        target_id = dictionary.get('targetId')
        target_name = dictionary.get('targetName')
        target_type = dictionary.get('targetType')
        tier_settings = cohesity_management_sdk.models_v2.archival_target_tier_info.ArchivalTargetTierInfo.from_dictionary(dictionary.get('tierSettings')) if dictionary.get('tierSettings') else None
        usage_type = dictionary.get('usageType')
        cancelled_app_objects_count = dictionary.get('cancelledAppObjectsCount')
        cancelled_objects_count = dictionary.get('cancelledObjectsCount')
        data_lock_constraints = cohesity_management_sdk.models_v2.data_lock_constraints.DataLockConstraints.from_dictionary(dictionary.get('dataLockConstraints')) if dictionary.get('dataLockConstraints') else None
        end_time_usecs = dictionary.get('endTimeUsecs')
        expiry_time_usecs = dictionary.get('expiryTimeUsecs')
        failed_app_objects_count = dictionary.get('failedAppObjectsCount')
        failed_objects_count = dictionary.get('failedObjectsCount')
        run_type = dictionary.get('runType')
        is_sla_violated = dictionary.get('isSlaViolated')
        snapshot_id = dictionary.get('snapshotId')
        start_time_usecs = dictionary.get('startTimeUsecs')
        queued_time_usecs = dictionary.get('queuedTimeUsecs')
        is_incremental = dictionary.get('isIncremental')
        is_forever_incremental = dictionary.get('isForeverIncremental')
        is_cad_archive = dictionary.get('isCadArchive')
        status = dictionary.get('status')
        message = dictionary.get('message')
        progress_task_id = dictionary.get('progressTaskId')
        stats_task_id = dictionary.get('statsTaskId')
        indexing_task_id = dictionary.get('indexingTaskId')
        successful_objects_count = dictionary.get('successfulObjectsCount')
        successful_app_objects_count = dictionary.get('successfulAppObjectsCount')
        stats = cohesity_management_sdk.models_v2.archival_data_statistics.ArchivalDataStatistics.from_dictionary(
            dictionary.get('stats')) if dictionary.get('stats') else None
        is_manually_deleted = dictionary.get('isManuallyDeleted')
        on_legal_hold = dictionary.get('onLegalHold')
        worm_properties = cohesity_management_sdk.models_v2.worm_archival_data.WormArchivalData.from_dictionary(dictionary.get('wormProperties')) if dictionary.get('wormProperties') else None

        # Return an object of this model
        return cls(archival_task_id,
                   ownership_context,
                   target_id,
                   target_name,
                   target_type,
                   tier_settings,
                   usage_type,
                   cancelled_app_objects_count,
                   cancelled_objects_count,
                   data_lock_constraints,
                   end_time_usecs,
                   expiry_time_usecs,
                   failed_app_objects_count,
                   failed_objects_count,
                   run_type,
                   is_sla_violated,
                   snapshot_id,
                   start_time_usecs,
                   queued_time_usecs,
                   is_incremental,
                   is_forever_incremental,
                   is_cad_archive,
                   status,
                   message,
                   progress_task_id,
                   stats_task_id,
                   indexing_task_id,
                   successful_objects_count,
                   successful_app_objects_count,
                   stats,
                   is_manually_deleted,
                   on_legal_hold,
                   worm_properties
                   )