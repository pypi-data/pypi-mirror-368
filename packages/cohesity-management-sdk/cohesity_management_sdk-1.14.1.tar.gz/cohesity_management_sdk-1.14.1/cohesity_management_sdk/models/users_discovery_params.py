# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class UsersDiscoveryParams(object):

    """Implementation of the 'UsersDiscoveryParams' model.

    Specifies discovery params for kUser entities. It should only be populated
    when the 'DiscoveryParams.discoverableObjectTypeList' includes 'kUsers'.


    Attributes:
        allow_chats_backup (bool): Specifies whether users' chats should be
            backed up or not. If this is false or not specified users' chats
            backup will not be done.
        discover_users_with_mailbox (bool): Specifies if office 365 users with
            valid mailboxes should be discovered or not.
        discover_users_with_onedrive (bool): Specifies if office 365 users with
            valid Onedrives should be discovered or not.
        fetch_mailbox_info (bool): Specifies whether users' mailbox info
            including the provisioning status, mailbox type & in-place archival
            support will be fetched and processed.
        fetch_one_drive_info (bool): Specifies whether users' onedrive info
            including the provisioning status & storage quota will be fetched
            and processed.
        skip_users_without_my_site (bool): Specifies whether to skip processing
            user who have uninitialized OneDrive or are without MySite.
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "allow_chats_backup": 'allowChatsBackup',
        "discover_users_with_mailbox":'discoverUsersWithMailbox',
        "discover_users_with_onedrive":'discoverUsersWithOnedrive',
        "fetch_mailbox_info": 'fetchMailboxInfo',
        "fetch_one_drive_info": 'fetchOneDriveInfo',
        "skip_users_without_my_site": 'skipUsersWithoutMySite'
    }
    def __init__(self,
                 allow_chats_backup=None,
                 discover_users_with_mailbox=None,
                 discover_users_with_onedrive=None,
                 fetch_mailbox_info=None,
                 fetch_one_drive_info=None,
                 skip_users_without_my_site=None
            ):

        """Constructor for the UsersDiscoveryParams class"""

        # Initialize members of the class
        self.allow_chats_backup = allow_chats_backup
        self.discover_users_with_mailbox = discover_users_with_mailbox
        self.discover_users_with_onedrive = discover_users_with_onedrive
        self.fetch_mailbox_info = fetch_mailbox_info
        self.fetch_one_drive_info = fetch_one_drive_info
        self.skip_users_without_my_site = skip_users_without_my_site

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
        allow_chats_backup = dictionary.get('allowChatsBackup')
        discover_users_with_mailbox = dictionary.get('discoverUsersWithMailbox')
        discover_users_with_onedrive = dictionary.get('discoverUsersWithOnedrive')
        fetch_mailbox_info = dictionary.get('fetchMailboxInfo')
        fetch_one_drive_info = dictionary.get('fetchOneDriveInfo')
        skip_users_without_my_site = dictionary.get('skipUsersWithoutMySite')

        # Return an object of this model
        return cls(
            allow_chats_backup,
            discover_users_with_mailbox,
            discover_users_with_onedrive,
            fetch_mailbox_info,
            fetch_one_drive_info,
            skip_users_without_my_site
)