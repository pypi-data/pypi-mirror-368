# -*- coding: utf-8 -*-


class PhysicalVolumeProtectionGroupObjectParams(object):

    """Implementation of the 'PhysicalVolumeProtectionGroupObjectParams' model.

    Specifies object parameters for creating physical volume Protection
    Groups.

    Attributes:
        id (long|int): Specifies the ID of the object protected.
        name (string): Specifies the name of the object protected.
        volume_guids (list of string): Specifies the list of GUIDs of volumes
            protected. If empty, then all volumes will be protected by
            default.
        enable_system_backup (bool): Specifies whether or not to take a system
            backup. Applicable only for windows sources.
        excluded_vss_writers (string): Specifies writer names which should be excluded from physical
          volume based backups for a given source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "volume_guids":'volumeGuids',
        "enable_system_backup":'enableSystemBackup',
        "excluded_vss_writers":'excludedVssWriters'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 volume_guids=None,
                 enable_system_backup=None,
                 excluded_vss_writers=None):
        """Constructor for the PhysicalVolumeProtectionGroupObjectParams class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.volume_guids = volume_guids
        self.enable_system_backup = enable_system_backup
        self.excluded_vss_writers = excluded_vss_writers


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
        volume_guids = dictionary.get('volumeGuids')
        enable_system_backup = dictionary.get('enableSystemBackup')
        excluded_vss_writers = dictionary.get('excludedVssWriters')

        # Return an object of this model
        return cls(id,
                   name,
                   volume_guids,
                   enable_system_backup,
                   excluded_vss_writers)