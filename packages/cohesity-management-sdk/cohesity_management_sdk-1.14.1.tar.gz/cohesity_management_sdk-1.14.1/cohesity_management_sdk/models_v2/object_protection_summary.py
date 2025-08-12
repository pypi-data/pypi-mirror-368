# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_type_v_center_params

class ObjectProtectionSummary(object):

    """Implementation of the 'ObjectProtectionSummary' model.

    Specifies the summary of a protected object.

    Attributes:
        id (long|int): Specifies object id.
        name (string): Specifies the name of the object.
        source_id (long|int): Specifies registered source id to which object
            belongs.
        source_name (string): Specifies registered source name to which object
            belongs.
        environment (EnvironmentEnum): Specifies the environment of the
            object.
        object_hash (string): Specifies the hash identifier of the object.
        object_type (ObjectType5Enum): Specifies the type of the object.
        logical_size_bytes (long|int): Specifies the logical size of object in
            bytes.
        uuid (string): Specifies the uuid which is a unique identifier of the
            object.
        protection_type (ProtectionType4Enum): Specifies the protection type
            of the object if any.
        os_type (OsTypeEnum): Specifies the operating system type of the
            object.
        v_center_summary (ObjectTypeVCenterParams): TODO: type description
            here.
        error (string): Specifies the error message if an error occurred
            during creation of the object protection.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "environment":'environment',
        "object_hash":'objectHash',
        "object_type":'objectType',
        "logical_size_bytes":'logicalSizeBytes',
        "uuid":'uuid',
        "protection_type":'protectionType',
        "os_type":'osType',
        "v_center_summary":'vCenterSummary',
        "error":'error'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 source_id=None,
                 source_name=None,
                 environment=None,
                 object_hash=None,
                 object_type=None,
                 logical_size_bytes=None,
                 uuid=None,
                 protection_type=None,
                 os_type=None,
                 v_center_summary=None,
                 error=None):
        """Constructor for the ObjectProtectionSummary class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.source_id = source_id
        self.source_name = source_name
        self.environment = environment
        self.object_hash = object_hash
        self.object_type = object_type
        self.logical_size_bytes = logical_size_bytes
        self.uuid = uuid
        self.protection_type = protection_type
        self.os_type = os_type
        self.v_center_summary = v_center_summary
        self.error = error


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
        name = dictionary.get('name')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        environment = dictionary.get('environment')
        object_hash = dictionary.get('objectHash')
        object_type = dictionary.get('objectType')
        logical_size_bytes = dictionary.get('logicalSizeBytes')
        uuid = dictionary.get('uuid')
        protection_type = dictionary.get('protectionType')
        os_type = dictionary.get('osType')
        v_center_summary = cohesity_management_sdk.models_v2.object_type_v_center_params.ObjectTypeVCenterParams.from_dictionary(dictionary.get('vCenterSummary')) if dictionary.get('vCenterSummary') else None
        error = dictionary.get('error')

        # Return an object of this model
        return cls(id,
                   name,
                   source_id,
                   source_name,
                   environment,
                   object_hash,
                   object_type,
                   logical_size_bytes,
                   uuid,
                   protection_type,
                   os_type,
                   v_center_summary,
                   error)


