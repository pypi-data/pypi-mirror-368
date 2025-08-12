# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.external_target_info

class IndexedObjectSnapshot(object):

    """Implementation of the 'IndexedObjectSnapshot' model.

    Specifies a snapshot containing the indexed object.

    Attributes:
        indexed_object_name (string): Specifies the indexed object name.
        object_snapshotid (string): Specifies snapshot id of the object
            containing this indexed object.
        snapshot_timestamp_usecs (long|int): Specifies a unix timestamp when
            the object snapshot was taken in micro seconds.
        run_type (RunTypeEnum): Specifies the type of protection run created
            this snapshot.
        protection_group_id (string): Specifies the protection group id which
            contains this snapshot.
        protection_group_name (string): Specifies the protection group name
            which contains this snapshot.
        storage_domain_id (long|int): Specifies the storage domain id
            containing this snapshot.
        attempts (long|int): Specifies the number of runs have been executed
            before the run completed successfully.
        size_bytes (long|int): Specifies the indexed object size in bytes.
        last_modified_time_usecs (long|int): Specifies the last time file was
            modified in unix timestamp.
        external_target_info (ExternalTargetInfo): Specifies the external
            target information if this is an archival snapshot.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "indexed_object_name":'indexedObjectName',
        "object_snapshotid":'objectSnapshotid',
        "snapshot_timestamp_usecs":'snapshotTimestampUsecs',
        "run_type":'runType',
        "protection_group_id":'protectionGroupId',
        "protection_group_name":'protectionGroupName',
        "storage_domain_id":'storageDomainId',
        "attempts":'attempts',
        "size_bytes":'sizeBytes',
        "last_modified_time_usecs":'lastModifiedTimeUsecs',
        "external_target_info":'externalTargetInfo'
    }

    def __init__(self,
                 indexed_object_name=None,
                 object_snapshotid=None,
                 snapshot_timestamp_usecs=None,
                 run_type=None,
                 protection_group_id=None,
                 protection_group_name=None,
                 storage_domain_id=None,
                 attempts=None,
                 size_bytes=None,
                 last_modified_time_usecs=None,
                 external_target_info=None):
        """Constructor for the IndexedObjectSnapshot class"""

        # Initialize members of the class
        self.indexed_object_name = indexed_object_name
        self.object_snapshotid = object_snapshotid
        self.snapshot_timestamp_usecs = snapshot_timestamp_usecs
        self.run_type = run_type
        self.protection_group_id = protection_group_id
        self.protection_group_name = protection_group_name
        self.storage_domain_id = storage_domain_id
        self.attempts = attempts
        self.size_bytes = size_bytes
        self.last_modified_time_usecs = last_modified_time_usecs
        self.external_target_info = external_target_info


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
        indexed_object_name = dictionary.get('indexedObjectName')
        object_snapshotid = dictionary.get('objectSnapshotid')
        snapshot_timestamp_usecs = dictionary.get('snapshotTimestampUsecs')
        run_type = dictionary.get('runType')
        protection_group_id = dictionary.get('protectionGroupId')
        protection_group_name = dictionary.get('protectionGroupName')
        storage_domain_id = dictionary.get('storageDomainId')
        attempts = dictionary.get('attempts')
        size_bytes = dictionary.get('sizeBytes')
        last_modified_time_usecs = dictionary.get('lastModifiedTimeUsecs')
        external_target_info = cohesity_management_sdk.models_v2.external_target_info.ExternalTargetInfo.from_dictionary(dictionary.get('externalTargetInfo')) if dictionary.get('externalTargetInfo') else None

        # Return an object of this model
        return cls(indexed_object_name,
                   object_snapshotid,
                   snapshot_timestamp_usecs,
                   run_type,
                   protection_group_id,
                   protection_group_name,
                   storage_domain_id,
                   attempts,
                   size_bytes,
                   last_modified_time_usecs,
                   external_target_info)


