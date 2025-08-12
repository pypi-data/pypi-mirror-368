# -*- coding: utf-8 -*-


class RunNowActionObjectLevelParams(object):

    """Implementation of the 'RunNowActionObjectLevelParams' model.

    Specifies the request parameters for RunNow action on a Protected object.

    Attributes:
        id (long|int): Specifies the ID of the object.
        name (string): Specifies the name of the object.
        take_local_snapshot_only (bool): If sepcified as true then runNow will
            only take local snapshot ignoring all other targets such as
            replication, archivals etc. If not sepcified or specified as false
            then runNow will follow the policy settings.
        backup_type (BackupTypeEnum): Specifies the backup type should be used
            for RunNow action.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "take_local_snapshot_only":'takeLocalSnapshotOnly',
        "backup_type":'backupType'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 take_local_snapshot_only=None,
                 backup_type=None):
        """Constructor for the RunNowActionObjectLevelParams class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.take_local_snapshot_only = take_local_snapshot_only
        self.backup_type = backup_type


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
        name = dictionary.get('name')
        take_local_snapshot_only = dictionary.get('takeLocalSnapshotOnly')
        backup_type = dictionary.get('backupType')

        # Return an object of this model
        return cls(id,
                   name,
                   take_local_snapshot_only,
                   backup_type)


