# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_info
import cohesity_management_sdk.models_v2.archival_target_info

class OwnerInfo(object):

    """Implementation of the 'OwnerInfo' model.

    Specifies the OneDrive owner info.

    Attributes:
        snapshot_id (string): Specifies the snapshot id.
        point_in_time_usecs (long|int): Specifies the timestamp (in
            microseconds. from epoch) for recovering to a point-in-time in the
            past.
        protection_group_id (string): Specifies the protection group id of the
            object snapshot.
        protection_group_name (string): Specifies the protection group name of
            the object snapshot.
        snapshot_creation_time_usecs (long|int): Specifies the time when the
            snapshot is created in Unix timestamp epoch in microseconds.
        object_info (ObjectInfo): Specifies the information about the object
            for which the snapshot is taken.
        snapshot_target_type (SnapshotTargetType3Enum): Specifies the snapshot
            target type.
        storage_domain_id (long|int): Specifies the ID of the Storage Domain
            where this snapshot is stored.
        archival_target_info (ArchivalTargetInfo): Specifies the archival
            target information if the snapshot is an archival snapshot.
        progress_task_id (string): Progress monitor task id for Recovery of
            VM.
        status (Status6Enum): Status of the Recovery. 'Running' indicates that
            the Recovery is still running. 'Canceled' indicates that the
            Recovery has been cancelled. 'Canceling' indicates that the
            Recovery is in the process of being cancelled. 'Failed' indicates
            that the Recovery has failed. 'Succeeded' indicates that the
            Recovery has finished successfully. 'SucceededWithWarning'
            indicates that the Recovery finished successfully, but there were
            some warning messages.
        start_time_usecs (long|int): Specifies the start time of the Recovery
            in Unix timestamp epoch in microseconds.
        end_time_usecs (long|int): Specifies the end time of the Recovery in
            Unix timestamp epoch in microseconds. This field will be populated
            only after Recovery is finished.
        messages (list of string): Specify error messages about the object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "snapshot_id":'snapshotId',
        "point_in_time_usecs":'pointInTimeUsecs',
        "protection_group_id":'protectionGroupId',
        "protection_group_name":'protectionGroupName',
        "snapshot_creation_time_usecs":'snapshotCreationTimeUsecs',
        "object_info":'objectInfo',
        "snapshot_target_type":'snapshotTargetType',
        "storage_domain_id":'storageDomainId',
        "archival_target_info":'archivalTargetInfo',
        "progress_task_id":'progressTaskId',
        "status":'status',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "messages":'messages'
    }

    def __init__(self,
                 snapshot_id=None,
                 point_in_time_usecs=None,
                 protection_group_id=None,
                 protection_group_name=None,
                 snapshot_creation_time_usecs=None,
                 object_info=None,
                 snapshot_target_type=None,
                 storage_domain_id=None,
                 archival_target_info=None,
                 progress_task_id=None,
                 status=None,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 messages=None):
        """Constructor for the OwnerInfo class"""

        # Initialize members of the class
        self.snapshot_id = snapshot_id
        self.point_in_time_usecs = point_in_time_usecs
        self.protection_group_id = protection_group_id
        self.protection_group_name = protection_group_name
        self.snapshot_creation_time_usecs = snapshot_creation_time_usecs
        self.object_info = object_info
        self.snapshot_target_type = snapshot_target_type
        self.storage_domain_id = storage_domain_id
        self.archival_target_info = archival_target_info
        self.progress_task_id = progress_task_id
        self.status = status
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.messages = messages


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
        snapshot_id = dictionary.get('snapshotId')
        point_in_time_usecs = dictionary.get('pointInTimeUsecs')
        protection_group_id = dictionary.get('protectionGroupId')
        protection_group_name = dictionary.get('protectionGroupName')
        snapshot_creation_time_usecs = dictionary.get('snapshotCreationTimeUsecs')
        object_info = cohesity_management_sdk.models_v2.object_info.ObjectInfo.from_dictionary(dictionary.get('objectInfo')) if dictionary.get('objectInfo') else None
        snapshot_target_type = dictionary.get('snapshotTargetType')
        storage_domain_id = dictionary.get('storageDomainId')
        archival_target_info = cohesity_management_sdk.models_v2.archival_target_info.ArchivalTargetInfo.from_dictionary(dictionary.get('archivalTargetInfo')) if dictionary.get('archivalTargetInfo') else None
        progress_task_id = dictionary.get('progressTaskId')
        status = dictionary.get('status')
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')
        messages = dictionary.get('messages')

        # Return an object of this model
        return cls(snapshot_id,
                   point_in_time_usecs,
                   protection_group_id,
                   protection_group_name,
                   snapshot_creation_time_usecs,
                   object_info,
                   snapshot_target_type,
                   storage_domain_id,
                   archival_target_info,
                   progress_task_id,
                   status,
                   start_time_usecs,
                   end_time_usecs,
                   messages)


