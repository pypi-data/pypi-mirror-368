# -*- coding: utf-8 -*-


class UpdateReplicationSnapshotConfig(object):

    """Implementation of the 'Update Replication Snapshot Config.' model.

    Specifies the configuration about updating an existing Replication
    Snapshot Run.

    Attributes:
        id (long|int): Specifies the cluster id of the replication cluster.
        enable_legal_hold (bool): Specifies whether to retain the snapshot for
            legal purpose. If set to true, the snapshots cannot be deleted
            until the retention period. Note that using this option may cause
            the Cluster to run out of space. If set to false explicitly, the
            hold is removed, and the snapshots will expire as specified in the
            policy of the Protection Group. If this field is not specified,
            there is no change to the hold of the run. This field can be set
            only by a User having Data Security Role.
        delete_snapshot (bool): Specifies whether to delete the snapshot. When
            this is set to true, all other params will be ignored.
        resync (bool): Specifies whether to retry the replication operation in
            case if earlier attempt failed. If not specified or set to false,
            replication is not retried.
        data_lock (DataLock2Enum): Specifies WORM retention type for the
            snapshots. When a WORM retention type is specified, the snapshots
            of the Protection Groups using this policy will be kept until the
            maximum of the snapshot retention time. During that time, the
            snapshots cannot be deleted.  'Compliance' implies WORM retention
            is set for compliance reason.  'Administrative' implies WORM
            retention is set for administrative purposes.
        days_to_keep (long|int): Specifies number of days to retain the
            snapshots. If positive, then this value is added to exisiting
            expiry time thereby increasing  the retention period of the
            snapshot. Conversly, if this value is negative, then value is
            subtracted to existing expiry time thereby decreasing the
            retention period of the snaphot. Here, by this operation if expiry
            time goes below current time then snapshot is immediately
            deleted.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "enable_legal_hold":'enableLegalHold',
        "delete_snapshot":'deleteSnapshot',
        "resync":'resync',
        "data_lock":'dataLock',
        "days_to_keep":'daysToKeep'
    }

    def __init__(self,
                 id=None,
                 enable_legal_hold=None,
                 delete_snapshot=None,
                 resync=None,
                 data_lock=None,
                 days_to_keep=None):
        """Constructor for the UpdateReplicationSnapshotConfig class"""

        # Initialize members of the class
        self.id = id
        self.enable_legal_hold = enable_legal_hold
        self.delete_snapshot = delete_snapshot
        self.resync = resync
        self.data_lock = data_lock
        self.days_to_keep = days_to_keep


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
        enable_legal_hold = dictionary.get('enableLegalHold')
        delete_snapshot = dictionary.get('deleteSnapshot')
        resync = dictionary.get('resync')
        data_lock = dictionary.get('dataLock')
        days_to_keep = dictionary.get('daysToKeep')

        # Return an object of this model
        return cls(id,
                   enable_legal_hold,
                   delete_snapshot,
                   resync,
                   data_lock,
                   days_to_keep)


