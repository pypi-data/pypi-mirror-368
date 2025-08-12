# -*- coding: utf-8 -*-


class CancelProtectionRunRequest(object):

    """Implementation of the 'Cancel protection run request.' model.

    Specifies the request to cancel a protection run.

    Attributes:
        local_task_id (string): Specifies the task id of the local run.
        object_ids (list of long|int): List of entity ids for which we need to
            cancel the backup tasks. If this is provided it will not cancel
            the complete run but will cancel only subset of backup tasks (if
            backup tasks are cancelled correspoding copy task will also get
            cancelled). If the backup tasks are completed successfully it will
            not cancel those backup tasks.
        replication_task_id (list of string): Specifies the task id of the
            replication run.
        archival_task_id (list of string): Specifies the task id of the
            archival run.
        cloud_spin_task_id (list of string): Specifies the task id of the
            cloudSpin run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "local_task_id":'localTaskId',
        "object_ids":'objectIds',
        "replication_task_id":'replicationTaskId',
        "archival_task_id":'archivalTaskId',
        "cloud_spin_task_id":'cloudSpinTaskId'
    }

    def __init__(self,
                 local_task_id=None,
                 object_ids=None,
                 replication_task_id=None,
                 archival_task_id=None,
                 cloud_spin_task_id=None):
        """Constructor for the CancelProtectionRunRequest class"""

        # Initialize members of the class
        self.local_task_id = local_task_id
        self.object_ids = object_ids
        self.replication_task_id = replication_task_id
        self.archival_task_id = archival_task_id
        self.cloud_spin_task_id = cloud_spin_task_id


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
        local_task_id = dictionary.get('localTaskId')
        object_ids = dictionary.get('objectIds')
        replication_task_id = dictionary.get('replicationTaskId')
        archival_task_id = dictionary.get('archivalTaskId')
        cloud_spin_task_id = dictionary.get('cloudSpinTaskId')

        # Return an object of this model
        return cls(local_task_id,
                   object_ids,
                   replication_task_id,
                   archival_task_id,
                   cloud_spin_task_id)


