# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.local_snapshot_statistics

class AttemptInformationForAnObject(object):

    """Implementation of the 'Attempt information for an object.' model.

    Specifies a backup attempt for an object.

    Attributes:
        start_time_usecs (long|int): Specifies the start time of attempt in
            Unix epoch Timestamp(in microseconds) for an object.
        end_time_usecs (long|int): Specifies the end time of attempt in Unix
            epoch Timestamp(in microseconds) for an object.
        admitted_time_usecs (long|int): Specifies the time at which the backup
            task was admitted to run in Unix epoch Timestamp(in microseconds)
            for an object.
        queue_duration_usecs (long|int): Specifies the duration between the startTime and when gatekeeper
          permit is granted to the backup task. If the backup task is rescheduled
          due to errors, the field is updated considering the time when permit is
          granted again. Queue duration = PermitGrantTimeUsecs - StartTimeUsecs
        permit_grant_time_usecs (long|int): Specifies the time when gatekeeper permit is granted to the backup
          task. If the backup task is rescheduled due to errors, the field is updated
          to the time when permit is granted again.
        snapshot_creation_time_usecs (long|int): Specifies the time at which
            the source snapshot was taken in Unix epoch Timestamp(in
            microseconds) for an object.
        status (Status3Enum): Status of the attempt for an object. 'Running'
            indicates that the run is still running. 'Canceled' indicates that
            the run has been canceled. 'Canceling' indicates that the run is
            in the process of being canceled. 'Failed' indicates that the run
            has failed. 'Missed' indicates that the run was unable to take
            place at the scheduled time because the previous run was still
            happening. 'Succeeded' indicates that the run has finished
            successfully. 'SucceededWithWarning' indicates that the run
            finished successfully, but there were some warning messages.
        stats (LocalSnapshotStatistics): Specifies statistics about local
            snapshot.
        progress_task_id (string): Progress monitor task for an object..
        message (string): A message about the error if encountered while
            performing backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "admitted_time_usecs":'admittedTimeUsecs',
        "queue_duration_usecs":'queueDurationUsecs',
        "permit_grant_time_usecs":'permitGrantTimeUsecs',
        "snapshot_creation_time_usecs":'snapshotCreationTimeUsecs',
        "status":'status',
        "stats":'stats',
        "progress_task_id":'progressTaskId',
        "message":'message'
    }

    def __init__(self,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 admitted_time_usecs=None,
                 queue_duration_usecs=None,
                 permit_grant_time_usecs=None,
                 snapshot_creation_time_usecs=None,
                 status=None,
                 stats=None,
                 progress_task_id=None,
                 message=None):
        """Constructor for the AttemptInformationForAnObject class"""

        # Initialize members of the class
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.admitted_time_usecs = admitted_time_usecs
        self.queue_duration_usecs = queue_duration_usecs
        self.permit_grant_time_usecs = permit_grant_time_usecs
        self.snapshot_creation_time_usecs = snapshot_creation_time_usecs
        self.status = status
        self.stats = stats
        self.progress_task_id = progress_task_id
        self.message = message


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
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')
        admitted_time_usecs = dictionary.get('admittedTimeUsecs')
        queue_duration_usecs = dictionary.get('queueDurationUsecs')
        permit_grant_time_usecs = dictionary.get('permitGrantTimeUsecs')
        snapshot_creation_time_usecs = dictionary.get('snapshotCreationTimeUsecs')
        status = dictionary.get('status')
        stats = cohesity_management_sdk.models_v2.local_snapshot_statistics.LocalSnapshotStatistics.from_dictionary(dictionary.get('stats')) if dictionary.get('stats') else None
        progress_task_id = dictionary.get('progressTaskId')
        message = dictionary.get('message')

        # Return an object of this model
        return cls(start_time_usecs,
                   end_time_usecs,
                   admitted_time_usecs,
                   queue_duration_usecs,
                   permit_grant_time_usecs,
                   snapshot_creation_time_usecs,
                   status,
                   stats,
                   progress_task_id,
                   message)