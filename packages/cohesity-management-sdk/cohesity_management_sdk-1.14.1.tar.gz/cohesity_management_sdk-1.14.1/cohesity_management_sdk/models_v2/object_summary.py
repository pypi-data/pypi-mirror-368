# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.object_string_identifier
import cohesity_management_sdk.models_v2.sharepoint_object_params
import cohesity_management_sdk.models_v2.object_type_v_center_params
import cohesity_management_sdk.models_v2.object_type_windows_cluster_params

class ObjectSummary(object):

    """Implementation of the 'Object Summary' model.

    Specifies the Object Summary.

    Attributes:
        entity_id (ObjectStringIdentifier): Specifies the string based Id for an object and also provides
          the history of ids assigned to the object
        environment (EnvironmentEnum): Specifies the environment of the
            object.
        id (long|int64): Specifies object id.
        name (string): Specifies the name of the object.
        source_id (long|int): Specifies registered source id to which object
            belongs.
        source_name (string): Specifies registered source name to which object
            belongs.
        child_objects (list of ObjectSummary): Specifies child object details.
        global_id (string): Specifies the global id which is a unique identifier of the
            object.
        logical_size_bytes (long|int): Specifies the logical size of object in bytes.
        object_hash (string): Specifies the hash identifier of the object.
        object_type (ObjectType5Enum): Specifies the type of the object.
        os_type (OsTypeEnum): Specifies the operating system type of the
            object.
        protection_type (ProtectionType11Enum): Specifies the protection type of the object if any.
        sharepoint_site_summary (SharepointObjectParams): Specifies the Sharepoint site object details.
        uuid (string): Specifies the uuid which is a unique identifier of the
            object.
        v_center_summary (ObjectTypeVCenterParams): Specifies the vCenter object details.
        windows_cluster_summary (ObjectTypeWindowsClusterParams): Specifies the windows cluster object details.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "entity_id":'entityId',
        "environment":'environment',
        "id": 'id',
        "name": 'name',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "child_objects":'childObjects',
        "global_id":'globalId',
        "logical_size_bytes":'logicalSizeBytes',
        "object_hash":'objectHash',
        "object_type":'objectType',
        "os_type":'osType',
        "protection_type":'protectionType',
        "sharepoint_site_summary":'sharepointSiteSummary',
        "uuid" : 'uuid' ,
        "v_center_summary":'vCenterSummary',
        "windows_cluster_summary":'windowsClusterSummary'
    }

    def __init__(self,
                 entity_id=None ,
                 environment=None ,
                 id=None ,
                 name=None ,
                 source_id=None ,
                 source_name=None,
                 child_objects=None,
                 global_id=None,
                 logical_size_bytes=None,
                 object_hash=None,
                 object_type=None,
                 os_type=None,
                 protection_type=None,
                 sharepoint_site_summary=None,
                 uuid=None,
                 v_center_summary=None,
                 windows_cluster_summary=None):
        """Constructor for the ObjectSummary class"""

        # Initialize members of the class
        self.entity_id = entity_id
        self.environment = environment
        self.id = id
        self.name = name
        self.source_id = source_id
        self.source_name = source_name
        self.child_objects = child_objects
        self.global_id = global_id
        self.logical_size_bytes = logical_size_bytes
        self.object_hash = object_hash
        self.object_type = object_type
        self.os_type = os_type
        self.protection_type = protection_type
        self.sharepoint_site_summary = sharepoint_site_summary
        self.uuid = uuid
        self.v_center_summary = v_center_summary
        self.windows_cluster_summary = windows_cluster_summary

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
        entity_id = cohesity_management_sdk.models_v2.object_string_identifier.ObjectStringIdentifier.from_dictionary(dictionary.get('entityId')) if dictionary.get('entityId') else None
        environment = dictionary.get('environment')
        id = dictionary.get('id')
        name = dictionary.get('name')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        child_objects = None
        if dictionary.get("childObjects") is not None:
            child_objects = list()
            for structure in dictionary.get('childObjects'):
                child_objects.append(cohesity_management_sdk.models_v2.object_summary.ObjectSummary.from_dictionary(structure))
        golbal_id = dictionary.get('globalId')
        logical_size_bytes = dictionary.get('logicalSizeBytes')
        object_hash = dictionary.get('objectHash')
        object_type = dictionary.get('objectType')
        os_type = dictionary.get('osType')
        protection_type = dictionary.get('protectionType')
        sharepoint_site_summary = cohesity_management_sdk.models_v2.sharepoint_object_params.SharepointObjectParams.from_dictionary(dictionary.get('sharepointSiteSummary')) if dictionary.get('sharepointSiteSummary') else None
        uuid = dictionary.get('uuid')
        v_center_summary = cohesity_management_sdk.models_v2.object_type_v_center_params.ObjectTypeVCenterParams.from_dictionary(dictionary.get('vCenterSummary')) if dictionary.get('vCenterSummary') else None
        windows_cluster_summary = cohesity_management_sdk.models_v2.object_type_windows_cluster_params.ObjectTypeWindowsClusterParams.from_dictionary(dictionary.get('windowsClusterSummary')) if dictionary.get('windowsClusterSummary') else None

        # Return an object of this model
        return cls(entity_id,
                   environment,
                   id,
                   name,
                   source_id,
                   source_name,
                   child_objects,
                   golbal_id,
                   logical_size_bytes,
                   object_hash,
                   object_type,
                   os_type,
                   protection_type,
                   sharepoint_site_summary,
                   uuid,
                   v_center_summary,
                   windows_cluster_summary)