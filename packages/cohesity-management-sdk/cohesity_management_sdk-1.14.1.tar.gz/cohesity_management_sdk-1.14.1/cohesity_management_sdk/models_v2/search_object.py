# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_type_v_center_params
import cohesity_management_sdk.models_v2.object_protection_stats_summary
import cohesity_management_sdk.models_v2.permissions_information
import cohesity_management_sdk.models_v2.vmware_object_entity_params
import cohesity_management_sdk.models_v2.object_information
import cohesity_management_sdk.models_v2.isilon_params
import cohesity_management_sdk.models_v2.netapp_params
import cohesity_management_sdk.models_v2.generic_nas_params
import cohesity_management_sdk.models_v2.flashblade_params_3
import cohesity_management_sdk.models_v2.elastifile_params
import cohesity_management_sdk.models_v2.gpfs_params
import cohesity_management_sdk.models_v2.mssql_params
import cohesity_management_sdk.models_v2.oracle_params
import cohesity_management_sdk.models_v2.tag_info
import cohesity_management_sdk.models_v2.snapshot_tag_info
import cohesity_management_sdk.models_v2.object_information
import cohesity_management_sdk.models_v2.object_protection_info

class SearchObject(object):

    """Implementation of the 'SearchObject' model.

    Specifies an object.

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
        protection_stats (list of ObjectProtectionStatsSummary): Specifies the
            count and size of protected and unprotected objects for the size.
        permissions (PermissionsInformation): Specifies the list of users,
            groups and users that have permissions for a given object.
        vmware_params (VmwareObjectEntityParams): Object details for Vmware.
        isilon_params (IsilonParams): Specifies the parameters for Isilon
            object.
        netapp_params (NetappParams): Specifies the parameters for NetApp
            object.
        generic_nas_params (GenericNasParams): Specifies the parameters for
            GenericNas object.
        flashblade_params (FlashbladeParams3): Specifies the parameters for
            Flashblade object.
        elastifile_params (ElastifileParams): Specifies the parameters for
            Elastifile object.
        gpfs_params (GpfsParams): Specifies the parameters for GPFS object.
        mssql_params (MssqlParams): Specifies the parameters for Msssql
            object.
        oracle_params (OracleParams): Specifies the parameters for Oracle
            object.
        tags (list of TagInfo): Specifies tag applied to the object.
        snapshot_tags (list of SnapshotTagInfo): Specifies snapshot tags
            applied to the object.
        source_info (ObjectInformation): Specifies the Source Object
            information.
        object_protection_infos (list of ObjectProtectionInfo): Specifies the
            object info on each cluster.

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
        "protection_stats":'protectionStats',
        "permissions":'permissions',
        "vmware_params":'vmwareParams',
        "isilon_params":'isilonParams',
        "netapp_params":'netappParams',
        "generic_nas_params":'genericNasParams',
        "flashblade_params":'flashbladeParams',
        "elastifile_params":'elastifileParams',
        "gpfs_params":'gpfsParams',
        "mssql_params":'mssqlParams',
        "oracle_params":'oracleParams',
        "tags":'tags',
        "snapshot_tags":'snapshotTags',
        "source_info":'sourceInfo',
        "object_protection_infos":'objectProtectionInfos'
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
                 protection_stats=None,
                 permissions=None,
                 vmware_params=None,
                 isilon_params=None,
                 netapp_params=None,
                 generic_nas_params=None,
                 flashblade_params=None,
                 elastifile_params=None,
                 gpfs_params=None,
                 mssql_params=None,
                 oracle_params=None,
                 tags=None,
                 snapshot_tags=None,
                 source_info=None,
                 object_protection_infos=None):
        """Constructor for the SearchObject class"""

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
        self.protection_stats = protection_stats
        self.permissions = permissions
        self.vmware_params = vmware_params
        self.isilon_params = isilon_params
        self.netapp_params = netapp_params
        self.generic_nas_params = generic_nas_params
        self.flashblade_params = flashblade_params
        self.elastifile_params = elastifile_params
        self.gpfs_params = gpfs_params
        self.mssql_params = mssql_params
        self.oracle_params = oracle_params
        self.tags = tags
        self.snapshot_tags = snapshot_tags
        self.source_info = source_info
        self.object_protection_infos = object_protection_infos


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
        protection_stats = None
        if dictionary.get("protectionStats") is not None:
            protection_stats = list()
            for structure in dictionary.get('protectionStats'):
                protection_stats.append(cohesity_management_sdk.models_v2.object_protection_stats_summary.ObjectProtectionStatsSummary.from_dictionary(structure))
        permissions = cohesity_management_sdk.models_v2.permissions_information.PermissionsInformation.from_dictionary(dictionary.get('permissions')) if dictionary.get('permissions') else None
        vmware_params = cohesity_management_sdk.models_v2.vmware_object_entity_params.VmwareObjectEntityParams.from_dictionary(dictionary.get('vmwareParams')) if dictionary.get('vmwareParams') else None
        isilon_params = cohesity_management_sdk.models_v2.isilon_params.IsilonParams.from_dictionary(dictionary.get('isilonParams')) if dictionary.get('isilonParams') else None
        netapp_params = cohesity_management_sdk.models_v2.netapp_params.NetappParams.from_dictionary(dictionary.get('netappParams')) if dictionary.get('netappParams') else None
        generic_nas_params = cohesity_management_sdk.models_v2.generic_nas_params.GenericNasParams.from_dictionary(dictionary.get('genericNasParams')) if dictionary.get('genericNasParams') else None
        flashblade_params = cohesity_management_sdk.models_v2.flashblade_params_3.FlashbladeParams3.from_dictionary(dictionary.get('flashbladeParams')) if dictionary.get('flashbladeParams') else None
        elastifile_params = cohesity_management_sdk.models_v2.elastifile_params.ElastifileParams.from_dictionary(dictionary.get('elastifileParams')) if dictionary.get('elastifileParams') else None
        gpfs_params = cohesity_management_sdk.models_v2.gpfs_params.GpfsParams.from_dictionary(dictionary.get('gpfsParams')) if dictionary.get('gpfsParams') else None
        mssql_params = cohesity_management_sdk.models_v2.mssql_params.MssqlParams.from_dictionary(dictionary.get('mssqlParams')) if dictionary.get('mssqlParams') else None
        oracle_params = cohesity_management_sdk.models_v2.oracle_params.OracleParams.from_dictionary(dictionary.get('oracleParams')) if dictionary.get('oracleParams') else None
        tags = None
        if dictionary.get("tags") is not None:
            tags = list()
            for structure in dictionary.get('tags'):
                tags.append(cohesity_management_sdk.models_v2.tag_info.TagInfo.from_dictionary(structure))
        snapshot_tags = None
        if dictionary.get("snapshotTags") is not None:
            snapshot_tags = list()
            for structure in dictionary.get('snapshotTags'):
                snapshot_tags.append(cohesity_management_sdk.models_v2.snapshot_tag_info.SnapshotTagInfo.from_dictionary(structure))
        source_info = cohesity_management_sdk.models_v2.object_information.Object.from_dictionary(dictionary.get('sourceInfo')) if dictionary.get('sourceInfo') else None
        object_protection_infos = None
        if dictionary.get("objectProtectionInfos") is not None:
            object_protection_infos = list()
            for structure in dictionary.get('objectProtectionInfos'):
                object_protection_infos.append(cohesity_management_sdk.models_v2.object_protection_info.ObjectProtectionInfo.from_dictionary(structure))

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
                   protection_stats,
                   permissions,
                   vmware_params,
                   isilon_params,
                   netapp_params,
                   generic_nas_params,
                   flashblade_params,
                   elastifile_params,
                   gpfs_params,
                   mssql_params,
                   oracle_params,
                   tags,
                   snapshot_tags,
                   source_info,
                   object_protection_infos)