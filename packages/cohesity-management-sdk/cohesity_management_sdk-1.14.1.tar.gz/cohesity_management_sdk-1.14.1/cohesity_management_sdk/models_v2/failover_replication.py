# -*- coding: utf-8 -*-


class FailoverReplication(object):

    """Implementation of the 'FailoverReplication' model.

    Specifies the details of a failover replication.

    Attributes:
        id (string): Specifies the replication id.
        status (Status23Enum): Specifies the replication status.
        error_message (string): Specifies the error details if replication
            status is 'Failed'.
        start_time_usecs (long|int): Specifies the replication start time in
            micro seconds.
        end_time_usecs (long|int): Specifies the replication complete time in
            micro seconds.
        percentage_completed (int): Specifies the percentage completed in the
            replication.
        logical_size_bytes (long|int): Specifies the total amount of logical
            data to be transferred for this replication.
        logical_bytes_transferred (long|int): Specifies the number of logical
            bytes transferred for this replication so far. This value can
            never exceed the total logical size of the replicated view.
        physical_bytes_transferred (long|int): Specifies the number of bytes
            sent over the wire for this replication so far.
        target_cluster_id (long|int): Specifies the failover target cluster
            id.
        target_cluster_incarnation_id (long|int): Specifies the failover
            target cluster incarnation id.
        target_cluster_name (string): Specifies the failover target cluster
            name.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "status":'status',
        "error_message":'errorMessage',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "percentage_completed":'percentageCompleted',
        "logical_size_bytes":'logicalSizeBytes',
        "logical_bytes_transferred":'logicalBytesTransferred',
        "physical_bytes_transferred":'physicalBytesTransferred',
        "target_cluster_id":'targetClusterId',
        "target_cluster_incarnation_id":'targetClusterIncarnationId',
        "target_cluster_name":'targetClusterName'
    }

    def __init__(self,
                 id=None,
                 status=None,
                 error_message=None,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 percentage_completed=None,
                 logical_size_bytes=None,
                 logical_bytes_transferred=None,
                 physical_bytes_transferred=None,
                 target_cluster_id=None,
                 target_cluster_incarnation_id=None,
                 target_cluster_name=None):
        """Constructor for the FailoverReplication class"""

        # Initialize members of the class
        self.id = id
        self.status = status
        self.error_message = error_message
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.percentage_completed = percentage_completed
        self.logical_size_bytes = logical_size_bytes
        self.logical_bytes_transferred = logical_bytes_transferred
        self.physical_bytes_transferred = physical_bytes_transferred
        self.target_cluster_id = target_cluster_id
        self.target_cluster_incarnation_id = target_cluster_incarnation_id
        self.target_cluster_name = target_cluster_name


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
        error_message = dictionary.get('errorMessage')
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')
        percentage_completed = dictionary.get('percentageCompleted')
        logical_size_bytes = dictionary.get('logicalSizeBytes')
        logical_bytes_transferred = dictionary.get('logicalBytesTransferred')
        physical_bytes_transferred = dictionary.get('physicalBytesTransferred')
        target_cluster_id = dictionary.get('targetClusterId')
        target_cluster_incarnation_id = dictionary.get('targetClusterIncarnationId')
        target_cluster_name = dictionary.get('targetClusterName')

        # Return an object of this model
        return cls(id,
                   status,
                   error_message,
                   start_time_usecs,
                   end_time_usecs,
                   percentage_completed,
                   logical_size_bytes,
                   logical_bytes_transferred,
                   physical_bytes_transferred,
                   target_cluster_id,
                   target_cluster_incarnation_id,
                   target_cluster_name)


