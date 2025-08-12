# -*- coding: utf-8 -*-


class ObjectBackupSnapshotStatusType(object):

    """Implementation of the 'Object Backup Snapshot Status type.' model.

    Object Backup Snapshot Status type.

    Attributes:
        object_backup_snapshot_status (ObjectBackupSnapshotStatusEnum):
            Specifies Object Backup Snapshot Status type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object_backup_snapshot_status":'objectBackupSnapshotStatus'
    }

    def __init__(self,
                 object_backup_snapshot_status=None):
        """Constructor for the ObjectBackupSnapshotStatusType class"""

        # Initialize members of the class
        self.object_backup_snapshot_status = object_backup_snapshot_status


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
        object_backup_snapshot_status = dictionary.get('objectBackupSnapshotStatus')

        # Return an object of this model
        return cls(object_backup_snapshot_status)


