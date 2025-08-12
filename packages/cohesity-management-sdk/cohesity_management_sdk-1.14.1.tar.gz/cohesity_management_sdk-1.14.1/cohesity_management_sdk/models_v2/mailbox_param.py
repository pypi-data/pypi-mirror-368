# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.folder_item

class MailboxParam(object):

    """Implementation of the 'MailboxParam' model.

    Specifies parameters to recover a Mailbox.

    Attributes:
        recover_entire_mailbox (bool): Specifies whether to recover the whole
            Mailbox.
        recover_folders (list of FolderItem): Specifies a list of email
            folders to recover.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recover_entire_mailbox":'recoverEntireMailbox',
        "recover_folders":'recoverFolders'
    }

    def __init__(self,
                 recover_entire_mailbox=None,
                 recover_folders=None):
        """Constructor for the MailboxParam class"""

        # Initialize members of the class
        self.recover_entire_mailbox = recover_entire_mailbox
        self.recover_folders = recover_folders


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
        recover_entire_mailbox = dictionary.get('recoverEntireMailbox')
        recover_folders = None
        if dictionary.get("recoverFolders") is not None:
            recover_folders = list()
            for structure in dictionary.get('recoverFolders'):
                recover_folders.append(cohesity_management_sdk.models_v2.folder_item.FolderItem.from_dictionary(structure))

        # Return an object of this model
        return cls(recover_entire_mailbox,
                   recover_folders)


