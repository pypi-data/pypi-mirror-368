# -*- coding: utf-8 -*-


class NetappRecoverFileAndFolderInfo(object):

    """Implementation of the 'NetappRecoverFileAndFolderInfo' model.

    Specifies the info about the netapp files and folders to be recovered.

    Attributes:
        absolute_path (string): Specifies the absolute path to the file or
            folder.
        destination_dir (string): Specifies the destination directory where
            the file/directory was copied.
        is_directory (bool): Specifies whether this is a directory or not.
        status (Status8Enum): Specifies the recovery status for this file or
            folder.
        messages (list of string): Specify error messages about the file
            during recovery.
        inode_id (long|int): Specifies the source inode number of the file
            being recovered.
        is_view_file_recovery (bool): Specify if the recovery is of type view file/folder.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "absolute_path":'absolutePath',
        "destination_dir":'destinationDir',
        "is_directory":'isDirectory',
        "status":'status',
        "messages":'messages',
        "inode_id":'inodeId',
        "is_view_file_recovery":'isViewFileRecovery'
    }

    def __init__(self,
                 absolute_path=None,
                 destination_dir=None,
                 is_directory=None,
                 status=None,
                 messages=None,
                 inode_id=None,
                 is_view_file_recovery=None
                 ):
        """Constructor for the NetappRecoverFileAndFolderInfo class"""

        # Initialize members of the class
        self.absolute_path = absolute_path
        self.destination_dir = destination_dir
        self.is_directory = is_directory
        self.status = status
        self.messages = messages
        self.inode_id = inode_id
        self.is_view_file_recovery = is_view_file_recovery


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
        absolute_path = dictionary.get('absolutePath')
        destination_dir = dictionary.get('destinationDir')
        is_directory = dictionary.get('isDirectory')
        status = dictionary.get('status')
        messages = dictionary.get('messages')
        inode_id = dictionary.get('inodeId')
        is_view_file_recovery = dictionary.get('isViewFileRecovery')

        # Return an object of this model
        return cls(absolute_path,
                   destination_dir,
                   is_directory,
                   status,
                   messages,
                   inode_id,
                   is_view_file_recovery)