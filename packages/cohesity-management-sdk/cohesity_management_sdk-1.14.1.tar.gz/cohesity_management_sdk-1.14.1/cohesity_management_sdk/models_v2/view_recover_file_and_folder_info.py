# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class ViewRecoverFileAndFolderInfo(object):
    """Implementation of the 'ViewRecoverFileAndFolderInfo' model.

    Specifies the info about the view files and folders to be recovered.

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
        is_view_file_recovery (bool): Specify if the recovery is of type view file/folder.
        inode_id (long|int): Specifies the source inode number of the file being recovered.
    """

    _names = {
        "absolute_path"         : 'absolutePath' ,
        "destination_dir"       : 'destinationDir' ,
        "is_directory"          : 'isDirectory' ,
        "status"                : 'status' ,
        "messages"              : 'messages' ,
        "is_view_file_recovery" : 'isViewFileRecovery',
        "inode_id":'inodeId'
    }

    def __init__(self,
                 absolute_path=None ,
                 destination_dir=None ,
                 is_directory=None ,
                 status=None ,
                 messages=None ,
                 is_view_file_recovery=None,
                 inode_id=None
                 ):
        """Constructor for the ViewRecoverFileAndFolderInfo class"""

        # Initialize members of the class
        self.absolute_path = absolute_path
        self.destination_dir = destination_dir
        self.is_directory = is_directory
        self.status = status
        self.messages = messages
        self.is_view_file_recovery = is_view_file_recovery
        self.inode_id = inode_id

    @classmethod
    def from_dictionary(cls, dictionary):
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
        absolute_path = dictionary.get('absolutePath')
        destination_dir = dictionary.get('destinationDir')
        is_directory = dictionary.get('isDirectory')
        status = dictionary.get('status')
        messages = dictionary.get('messages')
        is_view_file_recovery = dictionary.get('isViewFileRecovery')
        inode_id = dictionary.get('inodeId')

        return cls(
            absolute_path ,
            destination_dir ,
            is_directory ,
            status ,
            messages ,
            is_view_file_recovery,
            inode_id
        )