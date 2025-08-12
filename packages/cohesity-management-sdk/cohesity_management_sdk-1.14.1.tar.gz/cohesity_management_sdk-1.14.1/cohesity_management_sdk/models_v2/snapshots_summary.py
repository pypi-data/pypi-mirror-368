# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.external_target_info

class SnapshotsSummary(object):

    """Implementation of the 'SnapshotsSummary' model.

    Specifies a summary of the object snapshots.

    Attributes:
        snapshot_target_type (SnapshotTargetType1Enum): Specifies the target
            type where the Object's snapshot resides.
        external_target_info (ExternalTargetInfo): Specifies the external
            target information if this is an archival snapshot.
        snapshot_count (long|int): Specifies the number of snapshots of this
            type and target.
        latest_snapshot_timestamp_usecs (long|int): Specifies the timestamp in
            Unix time epoch in microseconds when the latest snapshot is
            taken.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "snapshot_target_type":'snapshotTargetType',
        "external_target_info":'externalTargetInfo',
        "snapshot_count":'snapshotCount',
        "latest_snapshot_timestamp_usecs":'latestSnapshotTimestampUsecs'
    }

    def __init__(self,
                 snapshot_target_type=None,
                 external_target_info=None,
                 snapshot_count=None,
                 latest_snapshot_timestamp_usecs=None):
        """Constructor for the SnapshotsSummary class"""

        # Initialize members of the class
        self.snapshot_target_type = snapshot_target_type
        self.external_target_info = external_target_info
        self.snapshot_count = snapshot_count
        self.latest_snapshot_timestamp_usecs = latest_snapshot_timestamp_usecs


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
        snapshot_target_type = dictionary.get('snapshotTargetType')
        external_target_info = cohesity_management_sdk.models_v2.external_target_info.ExternalTargetInfo.from_dictionary(dictionary.get('externalTargetInfo')) if dictionary.get('externalTargetInfo') else None
        snapshot_count = dictionary.get('snapshotCount')
        latest_snapshot_timestamp_usecs = dictionary.get('latestSnapshotTimestampUsecs')

        # Return an object of this model
        return cls(snapshot_target_type,
                   external_target_info,
                   snapshot_count,
                   latest_snapshot_timestamp_usecs)


