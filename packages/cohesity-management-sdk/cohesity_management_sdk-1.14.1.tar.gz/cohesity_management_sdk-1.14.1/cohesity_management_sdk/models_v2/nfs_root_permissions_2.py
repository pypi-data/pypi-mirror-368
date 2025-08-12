# -*- coding: utf-8 -*-


class NfsRootPermissions2(object):

    """Implementation of the 'NfsRootPermissions2' model.

    Specifies the NFS root permission config of the view file system.

    Attributes:
        gid (int): Unix GID for the root of the file system.
        mode (int): Unix mode bits for the root of the file system.
        uid (int): Unix UID for the root of the file system.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "gid":'gid',
        "mode":'mode',
        "uid":'uid'
    }

    def __init__(self,
                 gid=None,
                 mode=None,
                 uid=None):
        """Constructor for the NfsRootPermissions2 class"""

        # Initialize members of the class
        self.gid = gid
        self.mode = mode
        self.uid = uid


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
        gid = dictionary.get('gid')
        mode = dictionary.get('mode')
        uid = dictionary.get('uid')

        # Return an object of this model
        return cls(gid,
                   mode,
                   uid)


