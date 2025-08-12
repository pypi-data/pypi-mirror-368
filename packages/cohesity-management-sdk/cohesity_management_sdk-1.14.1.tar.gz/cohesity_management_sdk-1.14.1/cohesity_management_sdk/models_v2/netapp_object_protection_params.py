# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.snapshot_label
import cohesity_management_sdk.models_v2.continuous_snapshot_params

class NetappObjectProtectionParams(object):

    """Implementation of the 'NetappObjectProtectionParams' model.

    Specifies the parameters which are specific to Netapp object protection.

    Attributes:
        protocol (Protocol4Enum): Specifies the protocol of the NAS device
            being backed up.
        exclude_object_ids (list of long|int): Specifies the objects to be
            excluded in the Protection.
        snapshot_label (SnapshotLabel): Specifies the snapshot label for
            incremental and full backup of Secondary Netapp volumes
            (Data-Protect Volumes).
        backup_existing_snapshot (bool): Specifies that snapshot label is not
            set for Data-Protect Netapp Volumes backup. If field is set to
            true, existing oldest snapshot is used for backup and subsequent
            incremental will be selected in ascending order of snapshot create
            time on the source. If snapshot label is set, this field is set to
            false.
        continuous_snapshots (ContinuousSnapshotParams): Specifies the source
            snapshots to be taken even if there is a pending run in a
            protection group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protocol":'protocol',
        "exclude_object_ids":'excludeObjectIds',
        "snapshot_label":'snapshotLabel',
        "backup_existing_snapshot":'backupExistingSnapshot',
        "continuous_snapshots":'continuousSnapshots'
    }

    def __init__(self,
                 protocol=None,
                 exclude_object_ids=None,
                 snapshot_label=None,
                 backup_existing_snapshot=None,
                 continuous_snapshots=None):
        """Constructor for the NetappObjectProtectionParams class"""

        # Initialize members of the class
        self.protocol = protocol
        self.exclude_object_ids = exclude_object_ids
        self.snapshot_label = snapshot_label
        self.backup_existing_snapshot = backup_existing_snapshot
        self.continuous_snapshots = continuous_snapshots


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
        protocol = dictionary.get('protocol')
        exclude_object_ids = dictionary.get('excludeObjectIds')
        snapshot_label = cohesity_management_sdk.models_v2.snapshot_label.SnapshotLabel.from_dictionary(dictionary.get('snapshotLabel')) if dictionary.get('snapshotLabel') else None
        backup_existing_snapshot = dictionary.get('backupExistingSnapshot')
        continuous_snapshots = cohesity_management_sdk.models_v2.continuous_snapshot_params.ContinuousSnapshotParams.from_dictionary(dictionary.get('continuousSnapshots')) if dictionary.get('continuousSnapshots') else None

        # Return an object of this model
        return cls(protocol,
                   exclude_object_ids,
                   snapshot_label,
                   backup_existing_snapshot,
                   continuous_snapshots)


