# -*- coding: utf-8 -*-


class SourceHierarchyObjectSummaries(object):

    """Implementation of the 'SourceHierarchyObjectSummaries' model.

    Specifies the list of Object Summaries for Objects under a given Source.

    Attributes:
        id (long|int): Specifies object id.
        source_id (long|int): Specifies registered source id to which object
            belongs.
        source_name (string): Specifies registered source name to which object
            belongs.
        name (string): Specifies the name of the object.
        object_type (ObjectType5Enum): Specifies the type of the object.
        logical_size_bytes (long|int): Specifies the logical size of object in
            bytes.
        uuid (string): Specifies the uuid which is a unique identifier of the
            object.
        environment (Environment2Enum): Specifies the environment of the
            object.
        os_type (OsTypeEnum): Specifies the operating system type of the
            object.
        parent_id (long|int): Specifies the ID of the direct parent of this
            object in the source hierarchy.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "name":'name',
        "object_type":'objectType',
        "logical_size_bytes":'logicalSizeBytes',
        "uuid":'uuid',
        "environment":'environment',
        "os_type":'osType',
        "parent_id":'parentId'
    }

    def __init__(self,
                 id=None,
                 source_id=None,
                 source_name=None,
                 name=None,
                 object_type=None,
                 logical_size_bytes=None,
                 uuid=None,
                 environment=None,
                 os_type=None,
                 parent_id=None):
        """Constructor for the SourceHierarchyObjectSummaries class"""

        # Initialize members of the class
        self.id = id
        self.source_id = source_id
        self.source_name = source_name
        self.name = name
        self.object_type = object_type
        self.logical_size_bytes = logical_size_bytes
        self.uuid = uuid
        self.environment = environment
        self.os_type = os_type
        self.parent_id = parent_id


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
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        name = dictionary.get('name')
        object_type = dictionary.get('objectType')
        logical_size_bytes = dictionary.get('logicalSizeBytes')
        uuid = dictionary.get('uuid')
        environment = dictionary.get('environment')
        os_type = dictionary.get('osType')
        parent_id = dictionary.get('parentId')

        # Return an object of this model
        return cls(id,
                   source_id,
                   source_name,
                   name,
                   object_type,
                   logical_size_bytes,
                   uuid,
                   environment,
                   os_type,
                   parent_id)


