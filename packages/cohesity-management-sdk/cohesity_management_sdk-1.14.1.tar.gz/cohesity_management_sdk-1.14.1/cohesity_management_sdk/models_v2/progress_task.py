# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.progress_task_event

class ProgressTask(object):

    """Implementation of the 'Progress Task' model.

    This specifies the details about the Progress Task.

    Attributes:
        id (string): Specifies the task id of the Progress task.
        status (Status15Enum): Specifies the current status of the progress
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

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "status":'status',
        "percentage_completed":'percentageCompleted',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "expected_remaining_time_usecs":'expectedRemainingTimeUsecs',
        "events":'events'
    }

    def __init__(self,
                 id=None,
                 status=None,
                 percentage_completed=None,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 expected_remaining_time_usecs=None,
                 events=None):
        """Constructor for the ProgressTask class"""

        # Initialize members of the class
        self.id = id
        self.status = status
        self.percentage_completed = percentage_completed
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.expected_remaining_time_usecs = expected_remaining_time_usecs
        self.events = events


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

        # Return an object of this model
        return cls(id,
                   status,
                   percentage_completed,
                   start_time_usecs,
                   end_time_usecs,
                   expected_remaining_time_usecs,
                   events)


