# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source_info

class File(object):

    """Implementation of the 'File' model.

    Specifies a File.

    Attributes:
        name (string): Specifies the file name.
        path (string): Specifies the path to this file.
        mtype (Type14Enum): Specifies the file type.
        tags (list of string): Specifies the tags on this file.
        snapshot_tags (list of string): Specifies the snapshot tags of this
            file.
        protection_group_id (string): Specifies the protection group id which
            contains this file.
        protection_group_name (string): Specifies the protection group name
            which contains this file.
        storage_domain_id (long|int): Specifies the Storage Domain id where
            the backup data of Object is present.
        source_info (SourceInfo): Specifies the Source Object information.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "path":'path',
        "mtype":'type',
        "tags":'tags',
        "snapshot_tags":'snapshotTags',
        "protection_group_id":'protectionGroupId',
        "protection_group_name":'protectionGroupName',
        "storage_domain_id":'storageDomainId',
        "source_info":'sourceInfo'
    }

    def __init__(self,
                 name=None,
                 path=None,
                 mtype=None,
                 tags=None,
                 snapshot_tags=None,
                 protection_group_id=None,
                 protection_group_name=None,
                 storage_domain_id=None,
                 source_info=None):
        """Constructor for the File class"""

        # Initialize members of the class
        self.name = name
        self.path = path
        self.mtype = mtype
        self.tags = tags
        self.snapshot_tags = snapshot_tags
        self.protection_group_id = protection_group_id
        self.protection_group_name = protection_group_name
        self.storage_domain_id = storage_domain_id
        self.source_info = source_info


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
        mtype = dictionary.get('type')
        tags = dictionary.get('tags')
        snapshot_tags = dictionary.get('snapshotTags')
        protection_group_id = dictionary.get('protectionGroupId')
        protection_group_name = dictionary.get('protectionGroupName')
        storage_domain_id = dictionary.get('storageDomainId')
        source_info = cohesity_management_sdk.models_v2.source_info.SourceInfo.from_dictionary(dictionary.get('sourceInfo')) if dictionary.get('sourceInfo') else None

        # Return an object of this model
        return cls(name,
                   path,
                   mtype,
                   tags,
                   snapshot_tags,
                   protection_group_id,
                   protection_group_name,
                   storage_domain_id,
                   source_info)


