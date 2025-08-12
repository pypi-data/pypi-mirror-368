# -*- coding: utf-8 -*-
# Copyright 2022 Cohesity Inc.


class SnapshotDiffParams(object):

    """Implementation of the 'SnapshotDiffParams' model.

    Attributes:
        cluster_id (long|int): TODO Type description here.
        incarnation_id (long|int): TODO Type description here.
        partition_id (long|int): TODO Type description here.
        job_id (long|int): TODO Type description here.
        entity_type (EntityTypeEnum): TODO Type description here.
        base_snapshot_job_instance_id (long|int): TODO Type description here.
        base_snapshot_time_usecs (long|int): TODO Type description here.
        snapshot_job_instance_id (long|int): TODO Type description here.
        snapshot_time_usecs (long|int): TODO Type description here.
        page_number (long|int): TODO Type description here.
        page_size (long|int): TODO Type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cluster_id":'clusterId',
        "incarnation_id":'attachedDiskId',
        "partition_id":'partitionId',
        "job_id":'jobId',
        "entity_type":'entityType',
        "base_snapshot_job_instance_id":'baseSnapshotJobInstanceId',
        "base_snapshot_time_usecs":'baseSnapshotTimeUsecs',
        "snapshot_job_instance_id":'snapshotJobInstanceId',
        "snapshot_time_usecs":'snapshotTimeUsecs',
        "page_number":'pageNumber',
        "page_size":'pageSize'
    }

    def __init__(self,
                 cluster_id=None,
                 incarnation_id=None,
                 partition_id=None,
                 job_id=None,
                 entity_type=None,
                 base_snapshot_job_instance_id=None,
                 base_snapshot_time_usecs=None,
                 snapshot_job_instance_id=None,
                 snapshot_time_usecs=None,
                 page_number=None,
                 page_size=None):
        """Constructor for the SnapshotDiffParams class"""

        # Initialize members of the class
        self.cluster_id = cluster_id
        self.incarnation_id = incarnation_id
        self.partition_id = partition_id
        self.job_id = job_id
        self.entity_type = entity_type
        self.base_snapshot_job_instance_id = base_snapshot_job_instance_id
        self.base_snapshot_time_usecs = base_snapshot_time_usecs
        self.snapshot_job_instance_id = snapshot_job_instance_id
        self.snapshot_time_usecs = snapshot_time_usecs
        self.page_number = page_number
        self.page_size = page_size


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
        cluster_id = dictionary.get('clusterId')
        incarnation_id = dictionary.get('attachedDiskId')
        partition_id = dictionary.get('partitionId')
        job_id = dictionary.get('jobId')
        entity_type = dictionary.get('entityType')
        base_snapshot_job_instance_id = dictionary.get('baseSnapshotJobInstanceId')
        base_snapshot_time_usecs = dictionary.get('baseSnapshotTimeUsecs')
        snapshot_job_instance_id = dictionary.get('snapshotJobInstanceId')
        snapshot_time_usecs = dictionary.get('snapshotTimeUsecs')
        page_number = dictionary.get('pageNumber')
        page_size = dictionary.get('pageSize')

        # Return an object of this model
        return cls(cluster_id,
                   incarnation_id,
                   partition_id,
                   job_id,
                   entity_type,
                   base_snapshot_job_instance_id,
                   base_snapshot_time_usecs,
                   snapshot_job_instance_id,
                   snapshot_time_usecs,
                   page_number,
                   page_size)


