# -*- coding: utf-8 -*-


class ObjectArchivalSnapshotInformation(object):

    """Implementation of the 'Object Archival Snapshot Information' model.

    Specifies the Archival snapshot information for the object.

    Attributes:
        snapshot_id (string): Specifies the id of the archival snapshot for
            the object.
        logical_size_bytes (long|int): Specifies the logical size of this
            snapshot in bytes.
        target_id (long|int): Specifies the archival target ID.
        archival_task_id (string): Specifies the archival task id. This is a
            protection group UID which only applies when archival type is
            'Tape'.
        target_name (string): Specifies the archival target name.
        target_type (TargetType1Enum): Specifies the archival target type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "snapshot_id":'snapshotId',
        "logical_size_bytes":'logicalSizeBytes',
        "target_id":'targetId',
        "archival_task_id":'archivalTaskId',
        "target_name":'targetName',
        "target_type":'targetType'
    }

    def __init__(self,
                 snapshot_id=None,
                 logical_size_bytes=None,
                 target_id=None,
                 archival_task_id=None,
                 target_name=None,
                 target_type=None):
        """Constructor for the ObjectArchivalSnapshotInformation class"""

        # Initialize members of the class
        self.snapshot_id = snapshot_id
        self.logical_size_bytes = logical_size_bytes
        self.target_id = target_id
        self.archival_task_id = archival_task_id
        self.target_name = target_name
        self.target_type = target_type


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
        logical_size_bytes = dictionary.get('logicalSizeBytes')
        target_id = dictionary.get('targetId')
        archival_task_id = dictionary.get('archivalTaskId')
        target_name = dictionary.get('targetName')
        target_type = dictionary.get('targetType')

        # Return an object of this model
        return cls(snapshot_id,
                   logical_size_bytes,
                   target_id,
                   archival_task_id,
                   target_name,
                   target_type)


