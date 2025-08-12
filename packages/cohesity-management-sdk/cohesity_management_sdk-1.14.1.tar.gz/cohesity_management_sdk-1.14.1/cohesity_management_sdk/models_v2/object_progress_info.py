# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.progress_task_event
import cohesity_management_sdk.models_v2.progress_stats
import cohesity_management_sdk.models_v2.progress_task

class ObjectProgressInfo(object):

    """Implementation of the 'ObjectProgressInfo' model.

    Specifies the progress of an object.

    Attributes:
        id (long|int): Specifies object id.
        name (string): Specifies the name of the object.
        source_id (long|int): Specifies registered source id to which object
            belongs.
        source_name (string): Specifies registered source name to which object
            belongs.
        environment (EnvironmentEnum): Specifies the environment of the
            object.
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
        failed_attempts (list of ProgressTask): Specifies progress for failed
            attempts of this object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "environment":'environment',
        "status":'status',
        "percentage_completed":'percentageCompleted',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "expected_remaining_time_usecs":'expectedRemainingTimeUsecs',
        "events":'events',
        "stats":'stats',
        "failed_attempts":'failedAttempts'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 source_id=None,
                 source_name=None,
                 environment=None,
                 status=None,
                 percentage_completed=None,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 expected_remaining_time_usecs=None,
                 events=None,
                 stats=None,
                 failed_attempts=None):
        """Constructor for the ObjectProgressInfo class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.source_id = source_id
        self.source_name = source_name
        self.environment = environment
        self.status = status
        self.percentage_completed = percentage_completed
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.expected_remaining_time_usecs = expected_remaining_time_usecs
        self.events = events
        self.stats = stats
        self.failed_attempts = failed_attempts


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
        name = dictionary.get('name')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        environment = dictionary.get('environment')
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
        failed_attempts = None
        if dictionary.get("failedAttempts") is not None:
            failed_attempts = list()
            for structure in dictionary.get('failedAttempts'):
                failed_attempts.append(cohesity_management_sdk.models_v2.progress_task.ProgressTask.from_dictionary(structure))

        # Return an object of this model
        return cls(id,
                   name,
                   source_id,
                   source_name,
                   environment,
                   status,
                   percentage_completed,
                   start_time_usecs,
                   end_time_usecs,
                   expected_remaining_time_usecs,
                   events,
                   stats,
                   failed_attempts)


