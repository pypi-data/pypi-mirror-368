# -*- coding: utf-8 -*-


class MSSQLVolumeProtectionGroupContainerParams(object):

    """Implementation of the 'MSSQL Volume Protection Group Container Params' model.

    Specifies the host specific parameters for a host container in this
    protection group. Objects specified here should only be MSSQL root
    containers and will not be protected unless they are also specified in the
    'objects' list. This list is just for specifying source level settings.

    Attributes:
        host_id (long|int): Specifies the id of the host container on which
            databases are hosted.
        host_name (string): Specifies the name of the host container on which
            databases are hosted.
        volume_guids (list of string): Specifies the list of volume GUIDs to
            be protected. If not specified, all the volumes of the host will
            be protected. Note that volumes of host on which databases are
            hosted are protected even if its not mentioned in this list.
        enable_system_backup (bool): Specifies whether to enable system/bmr
            backup using 3rd party tools installed on agent host.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "host_id":'hostId',
        "host_name":'hostName',
        "volume_guids":'volumeGuids',
        "enable_system_backup":'enableSystemBackup'
    }

    def __init__(self,
                 host_id=None,
                 host_name=None,
                 volume_guids=None,
                 enable_system_backup=None):
        """Constructor for the MSSQLVolumeProtectionGroupContainerParams class"""

        # Initialize members of the class
        self.host_id = host_id
        self.host_name = host_name
        self.volume_guids = volume_guids
        self.enable_system_backup = enable_system_backup


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
        host_id = dictionary.get('hostId')
        host_name = dictionary.get('hostName')
        volume_guids = dictionary.get('volumeGuids')
        enable_system_backup = dictionary.get('enableSystemBackup')

        # Return an object of this model
        return cls(host_id,
                   host_name,
                   volume_guids,
                   enable_system_backup)


