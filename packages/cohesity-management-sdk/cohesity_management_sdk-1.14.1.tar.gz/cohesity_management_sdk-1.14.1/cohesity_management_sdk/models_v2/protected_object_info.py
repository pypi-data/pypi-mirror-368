# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_type_v_center_params
import cohesity_management_sdk.models_v2.tenant
import cohesity_management_sdk.models_v2.protected_object_backup_config
import cohesity_management_sdk.models_v2.protected_object_group_backup_config
import cohesity_management_sdk.models_v2.object_protection_run_summary
import cohesity_management_sdk.models_v2.sharepoint_object_params

class ProtectedObjectInfo(object):

    """Implementation of the 'ProtectedObjectInfo' model.

    Specifies the details of a protected object.

    Attributes:
        id (long|int): Specifies object id.
        name (string): Specifies the name of the object.
        source_id (long|int): Specifies registered source id to which object
            belongs.
        source_name (string): Specifies registered source name to which object
            belongs.
        environment (Environment2Enum): Specifies the environment of the
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
        sharepoint_site_summary (SharepointObjectParams):  Specifies the
            Sharepoint site object details.
        permissions (list of Tenant): Specifies the list of tenants that have
            permissions for this accessing given protected object.
        object_backup_configuration (ProtectedObjectBackupConfig): Specifies
            the backup configuration for protected object.
        protection_group_configurations (list of
            ProtectedObjectGroupBackupConfig): Specifies the protection info
            associated with every object. There can be multiple instances of
            protection info since the same object can be protected in multiple
            protection groups.
        last_run (ObjectProtectionRunSummary): Specifies the response body of
            the get object runs request.

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
        "sharepoint_site_summary": 'sharepointSiteSummary',
        "permissions":'permissions',
        "object_backup_configuration":'objectBackupConfiguration',
        "protection_group_configurations":'protectionGroupConfigurations',
        "last_run":'lastRun'
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
                 sharepoint_site_summary=None,
                 permissions=None,
                 object_backup_configuration=None,
                 protection_group_configurations=None,
                 last_run=None):
        """Constructor for the ProtectedObjectInfo class"""

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
        self.sharepoint_site_summary = sharepoint_site_summary
        self.v_center_summary = v_center_summary
        self.permissions = permissions
        self.object_backup_configuration = object_backup_configuration
        self.protection_group_configurations = protection_group_configurations
        self.last_run = last_run


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
        sharepoint_site_summary = cohesity_management_sdk.models_v2.sharepoint_object_params.SharepointObjectParams.from_dictionary(dictionary.get('sharepointSiteSummary')) if dictionary.get('sharepointSiteSummary') else None
        permissions = None
        if dictionary.get("permissions") is not None:
            permissions = list()
            for structure in dictionary.get('permissions'):
                permissions.append(cohesity_management_sdk.models_v2.tenant.Tenant.from_dictionary(structure))
        object_backup_configuration = cohesity_management_sdk.models_v2.protected_object_backup_config.ProtectedObjectBackupConfig.from_dictionary(dictionary.get('objectBackupConfiguration')) if dictionary.get('objectBackupConfiguration') else None
        protection_group_configurations = None
        if dictionary.get("protectionGroupConfigurations") is not None:
            protection_group_configurations = list()
            for structure in dictionary.get('protectionGroupConfigurations'):
                protection_group_configurations.append(cohesity_management_sdk.models_v2.protected_object_group_backup_config.ProtectedObjectGroupBackupConfig.from_dictionary(structure))
        last_run = cohesity_management_sdk.models_v2.object_protection_run_summary.ObjectProtectionRunSummary.from_dictionary(dictionary.get('lastRun')) if dictionary.get('lastRun') else None

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
                   sharepoint_site_summary,
                   permissions,
                   object_backup_configuration,
                   protection_group_configurations,
                   last_run)


