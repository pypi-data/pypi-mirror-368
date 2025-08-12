# -*- coding: utf-8 -*-

class CancelProtectionGroupRunRequest(object):

    """Implementation of the 'CancelProtectionGroupRunRequest' model.

    Specifies the request to cancel a protection run.

    Attributes:
        archival_task_id (list of string): Specifies the task id of the
            archival run.
        cloud_spin_task_id (list of string): Specifies the task id of the
            cloudSpin run.
        local_task_id (string): Specifies the task id of the local run.
        object_ids (list of long|int): List of entity ids for which we need to
            cancel the backup tasks. If this is provided it will not cancel the
            complete run but will cancel only subset of backup tasks (if backup
            tasks are cancelled correspoding copy task will also get cancelled).
            If the backup tasks are completed successfully it will not cancel
            those backup tasks.
        replication_task_id (list of long|int): Specifies the cluster
            identifiers where the tasks run. If specified, the archival target
            ids must be present within the run specified by the archivalTaskId
            above.
        run_id (list of string): Specifies a unique run id of the Protection
            Group run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "archival_task_id":'archivalTaskId',
        "cloud_spin_task_id":'cloudSpinTaskId',
        "local_task_id":'localTaskId',
        "object_ids": 'objectIds',
        "replication_task_id":'replicationTaskId',
        "run_id":'runId'
    }

    def __init__(self,
                 run_id,
                 archival_task_id=None,
                 cloud_spin_task_id=None,
                 local_task_id=None,
                 object_ids=None,
                 replication_task_id=None):
        """Constructor for the CancelProtectionGroupRunRequest class"""

        # Initialize members of the class
        self.archival_task_id = archival_task_id
        self.cloud_spin_task_id = cloud_spin_task_id
        self.local_task_id = local_task_id
        self.object_ids = object_ids
        self.replication_task_id = replication_task_id
        self.run_id = run_id


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
        cloud_spin_task_id = dictionary.get('cloudSpinTaskId')
        local_task_id = dictionary.get('localTaskId')
        object_ids = dictionary.get('objectIds')
        replication_task_id = dictionary.get('replicationTaskId')
        run_id = dictionary.get('runId')

        # Return an object of this model
        return cls(run_id,
                   archival_task_id,
                   cloud_spin_task_id,
                   local_task_id,
                   object_ids,
                   replication_task_id)


