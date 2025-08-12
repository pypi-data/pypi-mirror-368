# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.archival_target_tier_info
import cohesity_management_sdk.models_v2.progress_task_event
import cohesity_management_sdk.models_v2.progress_stats
import cohesity_management_sdk.models_v2.object_progress_info

class ArchivalTargetProgressInfo(object):

    """Implementation of the 'ArchivalTargetProgressInfo' model.

    Specifies the progress of an archival run target.

    Attributes:
        target_id (long|int): Specifies the archival target ID.
        archival_task_id (string): Specifies the archival task id. This is a
            protection group UID which only applies when archival type is
            'Tape'.
        target_name (string): Specifies the archival target name.
        target_type (TargetType1Enum): Specifies the archival target type.
        tier_settings (ArchivalTargetTierInfo): Specifies the tier info for
            archival.
        status (Status3Enum): Specifies the current status of the progress
            task.
        percentage_completed (float): Specifies the current completed
            percentage of the progress task.
        start_time_usecs (long|int): Specifies the start time of the progress
            task in Unix epoch Timestamp(in microseconds).
        end_time_usecs (long|int): Specifies the end time of the progress task
            in Unix epoch Timestamp(in microseconds).
        expected_remaining_time_usecs (long|int): Specifies the expected
            remaining time of the progress task in Unix epoch Timestamp(in
            microseconds).
        events (list of ProgressTaskEvent): Specifies the event log created
            for progress Task.
        stats (ProgressStats): Specifies the stats within progress.
        objects (list of ObjectProgressInfo): Specifies progress for objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_id":'targetId',
        "archival_task_id":'archivalTaskId',
        "target_name":'targetName',
        "target_type":'targetType',
        "tier_settings":'tierSettings',
        "status":'status',
        "percentage_completed":'percentageCompleted',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "expected_remaining_time_usecs":'expectedRemainingTimeUsecs',
        "events":'events',
        "stats":'stats',
        "objects":'objects'
    }

    def __init__(self,
                 target_id=None,
                 archival_task_id=None,
                 target_name=None,
                 target_type=None,
                 tier_settings=None,
                 status=None,
                 percentage_completed=None,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 expected_remaining_time_usecs=None,
                 events=None,
                 stats=None,
                 objects=None):
        """Constructor for the ArchivalTargetProgressInfo class"""

        # Initialize members of the class
        self.target_id = target_id
        self.archival_task_id = archival_task_id
        self.target_name = target_name
        self.target_type = target_type
        self.tier_settings = tier_settings
        self.status = status
        self.percentage_completed = percentage_completed
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.expected_remaining_time_usecs = expected_remaining_time_usecs
        self.events = events
        self.stats = stats
        self.objects = objects


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
        target_id = dictionary.get('targetId')
        archival_task_id = dictionary.get('archivalTaskId')
        target_name = dictionary.get('targetName')
        target_type = dictionary.get('targetType')
        tier_settings = cohesity_management_sdk.models_v2.archival_target_tier_info.ArchivalTargetTierInfo.from_dictionary(dictionary.get('tierSettings')) if dictionary.get('tierSettings') else None
        status = dictionary.get('status')
        percentage_completed = dictionary.get('percentageCompleted')
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')
        expected_remaining_time_usecs = dictionary.get('expectedRemainingTimeUsecs')
        events = None
        if dictionary.get("events") is not None:
            events = list()
            for structure in dictionary.get('events'):
                events.append(cohesity_management_sdk.models_v2.progress_task_event.ProgressTaskEvent.from_dictionary(structure))
        stats = cohesity_management_sdk.models_v2.progress_stats.ProgressStats.from_dictionary(dictionary.get('stats')) if dictionary.get('stats') else None
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.object_progress_info.ObjectProgressInfo.from_dictionary(structure))

        # Return an object of this model
        return cls(target_id,
                   archival_task_id,
                   target_name,
                   target_type,
                   tier_settings,
                   status,
                   percentage_completed,
                   start_time_usecs,
                   end_time_usecs,
                   expected_remaining_time_usecs,
                   events,
                   stats,
                   objects)


