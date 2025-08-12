# -*- coding: utf-8 -*-


class ProtectionRunSummary(object):

    """Implementation of the 'ProtectionRunSummary' model.

    Specifies the summary of a protection run.

    Attributes:
        id (string): Specifies the ID of the Protection Group run.
        protection_group_id (string): ProtectionGroupId to which this run
            belongs.
        protection_group_name (string): Name of the Protection Group to which
            this run belongs.
        environment (Environment6Enum): Specifies the environment type of the
            Protection Group.
        is_sla_violated (bool): Indicated if SLA has been violated for this
            run.
        start_time_usecs (long|int): Specifies the start time of backup run in
            Unix epoch Timestamp(in microseconds).
        end_time_usecs (long|int): Specifies the end time of backup run in
            Unix epoch Timestamp(in microseconds).
        status (Status5Enum): Status of the backup run. 'Running' indicates
            that the run is still running. 'Canceled' indicates that the run
            has been canceled. 'Canceling' indicates that the run is in the
            process of being canceled. 'Failed' indicates that the run has
            failed. 'Missed' indicates that the run was unable to take place
            at the scheduled time because the previous run was still
            happening. 'Succeeded' indicates that the run has finished
            successfully. 'SucceededWithWarning' indicates that the run
            finished successfully, but there were some warning messages.
        is_full_run (bool): Specifies if the protection run is a full run.
        total_objects_count (long|int): Specifies the total number of objects
            protected in this run.
        success_objects_count (long|int): Specifies the number of objects
            which are successfully protected in this run.
        logical_size_bytes (long|int): Specifies total logical size of
            object(s) in bytes.
        bytes_written (long|int): Specifies total size of data in bytes
            written after taking backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "protection_group_id":'protectionGroupId',
        "protection_group_name":'protectionGroupName',
        "environment":'environment',
        "is_sla_violated":'isSlaViolated',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "status":'status',
        "is_full_run":'isFullRun',
        "total_objects_count":'totalObjectsCount',
        "success_objects_count":'successObjectsCount',
        "logical_size_bytes":'logicalSizeBytes',
        "bytes_written":'bytesWritten'
    }

    def __init__(self,
                 id=None,
                 protection_group_id=None,
                 protection_group_name=None,
                 environment=None,
                 is_sla_violated=None,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 status=None,
                 is_full_run=None,
                 total_objects_count=None,
                 success_objects_count=None,
                 logical_size_bytes=None,
                 bytes_written=None):
        """Constructor for the ProtectionRunSummary class"""

        # Initialize members of the class
        self.id = id
        self.protection_group_id = protection_group_id
        self.protection_group_name = protection_group_name
        self.environment = environment
        self.is_sla_violated = is_sla_violated
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.status = status
        self.is_full_run = is_full_run
        self.total_objects_count = total_objects_count
        self.success_objects_count = success_objects_count
        self.logical_size_bytes = logical_size_bytes
        self.bytes_written = bytes_written


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
        protection_group_id = dictionary.get('protectionGroupId')
        protection_group_name = dictionary.get('protectionGroupName')
        environment = dictionary.get('environment')
        is_sla_violated = dictionary.get('isSlaViolated')
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')
        status = dictionary.get('status')
        is_full_run = dictionary.get('isFullRun')
        total_objects_count = dictionary.get('totalObjectsCount')
        success_objects_count = dictionary.get('successObjectsCount')
        logical_size_bytes = dictionary.get('logicalSizeBytes')
        bytes_written = dictionary.get('bytesWritten')

        # Return an object of this model
        return cls(id,
                   protection_group_id,
                   protection_group_name,
                   environment,
                   is_sla_violated,
                   start_time_usecs,
                   end_time_usecs,
                   status,
                   is_full_run,
                   total_objects_count,
                   success_objects_count,
                   logical_size_bytes,
                   bytes_written)


