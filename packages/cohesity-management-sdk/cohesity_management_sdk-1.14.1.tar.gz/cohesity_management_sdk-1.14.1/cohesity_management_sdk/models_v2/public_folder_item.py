# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source_info

class PublicFolderItem(object):

    """Implementation of the 'PublicFolderItem' model.

    Specifies an Public folder indexed item.

    Attributes:
        name (string): Specifies the name of the object.
        path (string): Specifies the path of the object.
        protection_group_id (string): Specifies the protection group id which
            contains this object.
        protection_group_name (string): Specifies the protection group name
            which contains this object.
        storage_domain_id (long|int): Specifies the Storage Domain id where
            the backup data of Object is present.
        source_info (SourceInfo): Specifies the Source Object information.
        mtype (string): Specifies the Public folder item type.
        id (string): Specifies the id of the indexed item.
        subject (string): Specifies the subject of the indexed item.
        has_attachments (bool): Specifies whether the item has any
            attachments
        item_class (string): Specifies the item class of the indexed item.
        received_time_secs (long|int): Specifies the Unix timestamp epoch in
            seconds at which this item is received.
        item_size (long|int): Specifies the size in bytes for the indexed
            item.
        parent_folder_id (string): Specifies the id of parent folder the
            indexed item.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "path":'path',
        "protection_group_id":'protectionGroupId',
        "protection_group_name":'protectionGroupName',
        "storage_domain_id":'storageDomainId',
        "source_info":'sourceInfo',
        "mtype":'type',
        "id":'id',
        "subject":'subject',
        "has_attachments":'hasAttachments',
        "item_class":'itemClass',
        "received_time_secs":'receivedTimeSecs',
        "item_size":'itemSize',
        "parent_folder_id":'parentFolderId'
    }

    def __init__(self,
                 name=None,
                 path=None,
                 protection_group_id=None,
                 protection_group_name=None,
                 storage_domain_id=None,
                 source_info=None,
                 mtype=None,
                 id=None,
                 subject=None,
                 has_attachments=None,
                 item_class=None,
                 received_time_secs=None,
                 item_size=None,
                 parent_folder_id=None):
        """Constructor for the PublicFolderItem class"""

        # Initialize members of the class
        self.name = name
        self.path = path
        self.protection_group_id = protection_group_id
        self.protection_group_name = protection_group_name
        self.storage_domain_id = storage_domain_id
        self.source_info = source_info
        self.mtype = mtype
        self.id = id
        self.subject = subject
        self.has_attachments = has_attachments
        self.item_class = item_class
        self.received_time_secs = received_time_secs
        self.item_size = item_size
        self.parent_folder_id = parent_folder_id


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
        name = dictionary.get('name')
        path = dictionary.get('path')
        protection_group_id = dictionary.get('protectionGroupId')
        protection_group_name = dictionary.get('protectionGroupName')
        storage_domain_id = dictionary.get('storageDomainId')
        source_info = cohesity_management_sdk.models_v2.source_info.SourceInfo.from_dictionary(dictionary.get('sourceInfo')) if dictionary.get('sourceInfo') else None
        mtype = dictionary.get('type')
        id = dictionary.get('id')
        subject = dictionary.get('subject')
        has_attachments = dictionary.get('hasAttachments')
        item_class = dictionary.get('itemClass')
        received_time_secs = dictionary.get('receivedTimeSecs')
        item_size = dictionary.get('itemSize')
        parent_folder_id = dictionary.get('parentFolderId')

        # Return an object of this model
        return cls(name,
                   path,
                   protection_group_id,
                   protection_group_name,
                   storage_domain_id,
                   source_info,
                   mtype,
                   id,
                   subject,
                   has_attachments,
                   item_class,
                   received_time_secs,
                   item_size,
                   parent_folder_id)


