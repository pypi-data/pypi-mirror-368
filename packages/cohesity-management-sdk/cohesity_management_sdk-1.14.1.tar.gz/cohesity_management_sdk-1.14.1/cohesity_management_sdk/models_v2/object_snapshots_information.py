# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.local_snapshot_info
import cohesity_management_sdk.models_v2.object_archival_snapshot_information

class ObjectSnapshotsInformation(object):

    """Implementation of the 'Object Snapshots Information.' model.

    Specifies the snapshots information for every Protection Group for a given
    object.

    Attributes:
        local_snapshot_info (LocalSnapshotInfo): Specifies the local snapshot
            information.
        archival_snapshots_info (list of ObjectArchivalSnapshotInformation):
            Specifies the archival snapshots information.
        indexing_status (IndexingStatusEnum): Specifies the indexing status of
            objects in this snapshot.<br> 'InProgress' indicates the indexing
            is in progress.<br> 'Done' indicates indexing is done.<br>
            'NoIndex' indicates indexing is not applicable.<br> 'Error'
            indicates indexing failed with error.
        protection_group_id (string): Specifies id of the Protection Group.
        protection_group_name (string): Specifies name of the Protection
            Group.
        run_instance_id (long|int): Specifies the instance id of the
            protection run which create the snapshot.
        source_group_id (string): Specifies the source protection group id in
            case of replication.
        storage_domain_id (long|int): Specifies the Storage Domain id where
            the backup data of Object is present.
        storage_domain_name (string): Specifies the name of Storage Domain id
            where the backup data of Object is present
        protection_run_id (string): Specifies the id of Protection Group Run.
        run_type (RunType1Enum): Specifies the type of protection run created
            this snapshot.
        protection_run_start_time_usecs (long|int): Specifies the start time
            of Protection Group Run in Unix timestamp epoch in microseconds.
        protection_run_end_time_usecs (long|int): Specifies the end time of
            Protection Group Run in Unix timestamp epoch in microseconds.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "local_snapshot_info":'localSnapshotInfo',
        "archival_snapshots_info":'archivalSnapshotsInfo',
        "indexing_status":'indexingStatus',
        "protection_group_id":'protectionGroupId',
        "protection_group_name":'protectionGroupName',
        "run_instance_id":'runInstanceId',
        "source_group_id":'sourceGroupId',
        "storage_domain_id":'storageDomainId',
        "storage_domain_name":'storageDomainName',
        "protection_run_id":'protectionRunId',
        "run_type":'runType',
        "protection_run_start_time_usecs":'protectionRunStartTimeUsecs',
        "protection_run_end_time_usecs":'protectionRunEndTimeUsecs'
    }

    def __init__(self,
                 local_snapshot_info=None,
                 archival_snapshots_info=None,
                 indexing_status=None,
                 protection_group_id=None,
                 protection_group_name=None,
                 run_instance_id=None,
                 source_group_id=None,
                 storage_domain_id=None,
                 storage_domain_name=None,
                 protection_run_id=None,
                 run_type=None,
                 protection_run_start_time_usecs=None,
                 protection_run_end_time_usecs=None):
        """Constructor for the ObjectSnapshotsInformation class"""

        # Initialize members of the class
        self.local_snapshot_info = local_snapshot_info
        self.archival_snapshots_info = archival_snapshots_info
        self.indexing_status = indexing_status
        self.protection_group_id = protection_group_id
        self.protection_group_name = protection_group_name
        self.run_instance_id = run_instance_id
        self.source_group_id = source_group_id
        self.storage_domain_id = storage_domain_id
        self.storage_domain_name = storage_domain_name
        self.protection_run_id = protection_run_id
        self.run_type = run_type
        self.protection_run_start_time_usecs = protection_run_start_time_usecs
        self.protection_run_end_time_usecs = protection_run_end_time_usecs


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
        local_snapshot_info = cohesity_management_sdk.models_v2.local_snapshot_info.LocalSnapshotInfo.from_dictionary(dictionary.get('localSnapshotInfo')) if dictionary.get('localSnapshotInfo') else None
        archival_snapshots_info = None
        if dictionary.get("archivalSnapshotsInfo") is not None:
            archival_snapshots_info = list()
            for structure in dictionary.get('archivalSnapshotsInfo'):
                archival_snapshots_info.append(cohesity_management_sdk.models_v2.object_archival_snapshot_information.ObjectArchivalSnapshotInformation.from_dictionary(structure))
        indexing_status = dictionary.get('indexingStatus')
        protection_group_id = dictionary.get('protectionGroupId')
        protection_group_name = dictionary.get('protectionGroupName')
        run_instance_id = dictionary.get('runInstanceId')
        source_group_id = dictionary.get('sourceGroupId')
        storage_domain_id = dictionary.get('storageDomainId')
        storage_domain_name = dictionary.get('storageDomainName')
        protection_run_id = dictionary.get('protectionRunId')
        run_type = dictionary.get('runType')
        protection_run_start_time_usecs = dictionary.get('protectionRunStartTimeUsecs')
        protection_run_end_time_usecs = dictionary.get('protectionRunEndTimeUsecs')

        # Return an object of this model
        return cls(local_snapshot_info,
                   archival_snapshots_info,
                   indexing_status,
                   protection_group_id,
                   protection_group_name,
                   run_instance_id,
                   source_group_id,
                   storage_domain_id,
                   storage_domain_name,
                   protection_run_id,
                   run_type,
                   protection_run_start_time_usecs,
                   protection_run_end_time_usecs)


