# -*- coding: utf-8 -*-


class DatastoreMigrationInfo(object):

    """Implementation of the 'DatastoreMigrationInfo' model.

    Specifies the info about datastore migration. This is only applicable for
    RecoverVm.

    Attributes:
        progress_task_id (string): Specifies the progress monitor path.
        status (Status14Enum): Specifies the status of the recovery.
        start_time_usecs (long|int): Specifies the start time in Unix
            timestamp epoch in microseconds.
        end_time_usecs (long|int): Specifies the end time in Unix timestamp
            epoch in microseconds.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "progress_task_id":'progressTaskId',
        "status":'status',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs'
    }

    def __init__(self,
                 progress_task_id=None,
                 status=None,
                 start_time_usecs=None,
                 end_time_usecs=None):
        """Constructor for the DatastoreMigrationInfo class"""

        # Initialize members of the class
        self.progress_task_id = progress_task_id
        self.status = status
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs


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
        progress_task_id = dictionary.get('progressTaskId')
        status = dictionary.get('status')
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')

        # Return an object of this model
        return cls(progress_task_id,
                   status,
                   start_time_usecs,
                   end_time_usecs)


