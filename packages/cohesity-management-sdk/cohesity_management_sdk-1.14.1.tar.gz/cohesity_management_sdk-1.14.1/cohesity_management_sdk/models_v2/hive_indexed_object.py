# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source_info

class HiveIndexedObject(object):

    """Implementation of the 'HiveIndexedObject' model.

    Specifies a Hive indexed object.

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
        mtype (Type17Enum): Specifies the Hive Object Type.
        id (string): Specifies the id of the indexed object.

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
        "id":'id'
    }

    def __init__(self,
                 name=None,
                 path=None,
                 protection_group_id=None,
                 protection_group_name=None,
                 storage_domain_id=None,
                 source_info=None,
                 mtype=None,
                 id=None):
        """Constructor for the HiveIndexedObject class"""

        # Initialize members of the class
        self.name = name
        self.path = path
        self.protection_group_id = protection_group_id
        self.protection_group_name = protection_group_name
        self.storage_domain_id = storage_domain_id
        self.source_info = source_info
        self.mtype = mtype
        self.id = id


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

        # Return an object of this model
        return cls(name,
                   path,
                   protection_group_id,
                   protection_group_name,
                   storage_domain_id,
                   source_info,
                   mtype,
                   id)


