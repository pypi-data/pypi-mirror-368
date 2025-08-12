# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.object_summary
import cohesity_management_sdk.models_v2.common_nas_object_params
import cohesity_management_sdk.models_v2.object_string_identifier
import cohesity_management_sdk.models_v2.object_type_v_center_params
import cohesity_management_sdk.models_v2.object_type_windows_cluster_params
import cohesity_management_sdk.models_v2.flashblade_object_params
import cohesity_management_sdk.models_v2.group_object_entity_params
import cohesity_management_sdk.models_v2.mongo_db_object_params
import cohesity_management_sdk.models_v2.mssql_object_entity_params
import cohesity_management_sdk.models_v2.netapp_object_params
import cohesity_management_sdk.models_v2.object_protection_stats_summary
import cohesity_management_sdk.models_v2.oracle_object_entity_params
import cohesity_management_sdk.models_v2.permissions_information
import cohesity_management_sdk.models_v2.isilon_params_1
import cohesity_management_sdk.models_v2.physical_object_entity_params
import cohesity_management_sdk.models_v2.sharepoint_object_entity_params
import cohesity_management_sdk.models_v2.sharepoint_object_params
import cohesity_management_sdk.models_v2.uda_object_params
import cohesity_management_sdk.models_v2.view_object_params
import cohesity_management_sdk.models_v2.vmware_object_entity_params


class Object(object) :
    """Implementation of the 'Object' model.

    Specifies information about an object.

    Attributes:
        child_objects (list of ObjectSummary): Specifies child object details.
        elastifile_params (CommonNasObjectParams): Specifies type of the object activity.
        entity_id (ObjectStringIdentifier): Specifies the string based Id for an object and also provides
          the history of ids assigned to the object
        environment (EnvironmentEnum): Specifies the environment of the
            object.
        flashblade_params (FlashbladeObjectParams): Specifies the parameters for
            Flashblade object.
        generic_nas_params (CommonNasObjectParams): Specifies the parameters for GenericNas object.
        global_id (string): Specifies the global id which is a unique identifier of the
            object.
        gpfs_params (CommonNasObjectParams): Specifies the parameters for GPFS object.
        group_params (GroupObjectEntityParams): Specifies the parameters for M365 Group object.
        id (long|int64): Specifies object id.
        isilon_params (IsilonParams1): Specifies the parameters for Isilon object.
        logical_size_bytes (long|int): Specifies the logical size of object in bytes.
        mongo_db_params (MongoDBObjectParams): Specifies the parameters for MongoDB object.
        mssql_params (MssqlObjectEntityParams): MssqlObjectEntityParams
        name (string): Specifies the name of the object.
        netapp_params (NetappObjectParams): Specifies the parameters for NetApp object.
        object_hash (string): Specifies the hash identifier of the object.
        object_type (ObjectType5Enum): Specifies the type of the object.
        oracle_params (OracleObjectEntityParams): Specifies the parameters for Oracle object.
        os_type (OsTypeEnum): Specifies the operating system type of the
            object.
        permissions (PermissionInfo): Specifies the list of users, groups and tenants that have permissions
            for this object.
        physical_params (PhysicalObjectEntityParams): PhysicalObjectEntityParams
        protection_stats (list of ObjectProtectionStatsSummary): Specifies the count and size of protected and unprotected objects
            for the size.
        protection_type (ProtectionType11Enum): Specifies the protection type of the object if any.
        sharepoint_params (SharepointObjectEntityParams): Specifies the parameters for Sharepoint object.
        sharepoint_site_summary (SharepointObjectParams): Specifies the Sharepoint site object details.
        source_id (long|int): Specifies registered source id to which object
            belongs.
        source_name (string): Specifies registered source name to which object
            belongs.
        uda_params (UdaObjectParams): Specifies the parameters for UDA object.
        uuid (string): Specifies the uuid which is a unique identifier of the
            object.
        v_center_summary (ObjectTypeVCenterParams): Specifies the vCenter object details.
        view_params (ViewObjectParams): Specifies the parameters for a View.
        vmware_params (VmwareObjectEntityParams): Specifies the parameters which are specific to VMware objects.
        windows_cluster_summary (ObjectTypeWindowsClusterParams): Specifies the windows cluster object details.




    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id"                       : 'id' ,
        "name"                     : 'name' ,
        "source_id"                : 'sourceId' ,
        "source_name"              : 'sourceName' ,
        "environment"              : 'environment',
        "entity_id"                : 'entityId' ,
        "object_type"              : 'objectType' ,
        "object_hash"              : 'objectHash' ,
        "logical_size_bytes"       : 'logicalSizeBytes' ,
        "uuid"                     : 'uuid' ,
        "global_id"                : 'globalId' ,
        "protection_type"          : 'protectionType' ,
        "os_type"                  : 'osType' ,
        "v_center_summary"         : 'vCenterSummary' ,
        "share_point_site_summary" : 'sharepointSiteSummary' ,
        "windows_cluster_summary"  : 'windowsClusterSummary' ,
        "child_objects"            : 'childObjects' ,
        "protection_stats"         : 'protectionStats' ,
        "permissions"              : 'permissions' ,
        "vmware_params"            : 'vmwareParams' ,
        "isilon_params"            : 'isilonParams' ,
        "netapp_params"            : 'netappParams' ,
        "generic_nas_params"       : 'genericNasParams' ,
        "flashblade_params"        : 'flashbladeParams' ,
        "elastifile_params"        : 'elastifileParams' ,
        "gpfs_params"              : 'gpfsParams' ,
        "mssql_params"             : 'mssqlParams' ,
        "oracle_params"            : 'oracleParams' ,
        "physical_params"          : 'physicalParams' ,
        "sharepoint_params"        : 'sharepointParams' ,
        "group_params"             : 'groupParams' ,
        "uda_params"               : 'udaParams' ,
        "view_params"              : 'viewParams' ,
        "mongo_db_params"          : 'mongoDBParams'
    }

    def __init__(self ,
                 id=None ,
                 name=None ,
                 source_id=None ,
                 source_name=None ,
                 environment=None ,
                 entity_id=None ,
                 object_type=None ,
                 object_hash=None ,
                 logical_size_bytes=None ,
                 uuid=None ,
                 global_id=None ,
                 protection_type=None ,
                 os_type=None ,
                 v_center_summary=None ,
                 share_point_site_summary=None ,
                 windows_cluster_summary=None ,
                 child_objects=None ,
                 protection_stats=None ,
                 permissions=None ,
                 vmware_params=None ,
                 isilon_params=None ,
                 netapp_params=None ,
                 generic_nas_params=None ,
                 flashblade_params=None ,
                 elastifile_params=None ,
                 gpfs_params=None ,
                 mssql_params=None ,
                 oracle_params=None ,
                 physical_params=None ,
                 sharepoint_params=None ,
                 group_params=None ,
                 uda_params=None ,
                 view_params=None ,
                 mongo_db_params=None
                 ) :
        """Constructor for the ObjectActivityType class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.source_id = source_id
        self.source_name = source_name
        self.environment = environment
        self.entity_id = entity_id
        self.object_type = object_type
        self.object_hash = object_hash
        self.logical_size_bytes = logical_size_bytes
        self.uuid = uuid
        self.global_id = global_id
        self.protection_type = protection_type
        self.os_type = os_type
        self.v_center_summary = v_center_summary
        self.share_point_site_summary = share_point_site_summary
        self.windows_cluster_summary = windows_cluster_summary
        self.child_objects = child_objects
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
        self.physical_params = physical_params
        self.sharepoint_params = sharepoint_params
        self.group_params = group_params
        self.uda_params = uda_params
        self.view_params = view_params
        self.mongo_db_params = mongo_db_params

    @classmethod
    def from_dictionary(cls ,
                        dictionary) :
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None :
            return None

        # Extract variables from the dictionary
        id = dictionary.get('id')
        name = dictionary.get('name')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        environment = dictionary.get('environment')
        entity_id = cohesity_management_sdk.models_v2.object_string_identifier.ObjectStringIdentifier.from_dictionary(
            dictionary.get('entityId')) if dictionary.get('entityId') else None
        object_type = dictionary.get('objectType')
        object_hash = dictionary.get('objectHash')
        logical_size_bytes = dictionary.get('logicalSizeBytes')
        uuid = dictionary.get('uuid')
        global_id = dictionary.get('globalId')
        protection_type = dictionary.get('protectionType')
        os_type = dictionary.get('osType')
        v_center_summary = cohesity_management_sdk.models_v2.object_type_v_center_params.ObjectTypeVCenterParams.from_dictionary(
            dictionary.get('vCenterSummary')) if dictionary.get('vCenterSummary') else None
        share_point_site_summary = cohesity_management_sdk.models_v2.sharepoint_object_params.SharepointObjectParams.from_dictionary(dictionary.get('sharepointSiteSummary')) if dictionary.get('sharepointSiteSummary') else None
        windows_cluster_summary = cohesity_management_sdk.models_v2.object_type_windows_cluster_params.ObjectTypeWindowsClusterParams.from_dictionary(
            dictionary.get('windowsClusterSummary')) if dictionary.get('windowsClusterSummary') else None
        child_objects = None
        if dictionary.get("childObjects") is not None :
            child_objects = list()
            for structure in dictionary.get('childObjects') :
                child_objects.append(
                    cohesity_management_sdk.models_v2.object_summary.ObjectSummary.from_dictionary(structure))
        protection_stats = None
        if dictionary.get("protectionStats") is not None :
            protection_stats = list()
            for structure in dictionary.get('protectionStats') :
                protection_stats.append(
                    cohesity_management_sdk.models_v2.object_protection_stats_summary.ObjectProtectionStatsSummary.from_dictionary(
                        structure))
        permissions = cohesity_management_sdk.models_v2.permissions_information.PermissionsInformation.from_dictionary(
            dictionary.get('permissions')) if dictionary.get('permissions') else None
        vmware_params = cohesity_management_sdk.models_v2.vmware_object_entity_params.VmwareObjectEntityParams.from_dictionary(
            dictionary.get('vmwareParams')) if dictionary.get('vmwareParams') else None
        isilon_params = cohesity_management_sdk.models_v2.isilon_params_1.IsilonParams1.from_dictionary(
            dictionary.get('isilonParams')) if dictionary.get('isilonParams') else None
        netapp_params = cohesity_management_sdk.models_v2.netapp_object_params.NetappObjectParams.from_dictionary(
            dictionary.get('netappParams')) if dictionary.get('netappParams') else None
        generic_nas_params = cohesity_management_sdk.models_v2.common_nas_object_params.CommonNasObjectParams.from_dictionary(
            dictionary.get('genericNasParams')) if dictionary.get('genericNasParams') else None
        flashblade_params = cohesity_management_sdk.models_v2.flashblade_object_params.FlashbladeObjectParams.from_dictionary(
            dictionary.get('flashbladeParams')) if dictionary.get('flashbladeParams') else None
        elastifile_params = cohesity_management_sdk.models_v2.common_nas_object_params.CommonNasObjectParams.from_dictionary(
            dictionary.get('elastifileParams')) if dictionary.get('elastifileParams') else None
        gpfs_params = cohesity_management_sdk.models_v2.common_nas_object_params.CommonNasObjectParams.from_dictionary(
            dictionary.get('gpfsParams')) if dictionary.get('gpfsParams') else None
        mssql_params = cohesity_management_sdk.models_v2.mssql_object_entity_params.MssqlObjectEntityParams.from_dictionary(
            dictionary.get('mssqlParams')) if dictionary.get('mssqlParams') else None
        oracle_params = cohesity_management_sdk.models_v2.oracle_object_entity_params.OracleObjectEntityParams.from_dictionary(
            dictionary.get('oracleParams')) if dictionary.get('oracleParams') else None
        physical_params = cohesity_management_sdk.models_v2.physical_object_entity_params.PhysicalObjectEntityParams.from_dictionary(
            dictionary.get('physicalParams')) if dictionary.get('physicalParams') else None
        sharepoint_params = cohesity_management_sdk.models_v2.sharepoint_object_entity_params.SharepointObjectEntityParams.from_dictionary(
            dictionary.get('sharepointParams')) if dictionary.get('sharepointParams') else None
        group_params = cohesity_management_sdk.models_v2.group_object_entity_params.GroupObjectEntityParams.from_dictionary(
            dictionary.get('groupParams')) if dictionary.get('groupParams') else None
        uda_params = cohesity_management_sdk.models_v2.uda_object_params.UdaObjectParams.from_dictionary(
            dictionary.get('udaParams')) if dictionary.get('udaParams') else None
        view_params = cohesity_management_sdk.models_v2.view_object_params.ViewObjectParams.from_dictionary(
            dictionary.get('viewParams')) if dictionary.get('viewParams') else None
        mongo_db_params = cohesity_management_sdk.models_v2.mongo_db_object_params.MongoDBObjectParams.from_dictionary(
            dictionary.get('mongoDBParams')) if dictionary.get('mongoDBParams') else None

        # Return an object of this model
        return cls(id ,
                   name ,
                   source_id ,
                   source_name ,
                   environment ,
                   entity_id ,
                   object_type ,
                   object_hash ,
                   logical_size_bytes ,
                   uuid ,
                   global_id ,
                   protection_type ,
                   os_type ,
                   v_center_summary ,
                   share_point_site_summary ,
                   windows_cluster_summary ,
                   child_objects ,
                   protection_stats ,
                   permissions ,
                   vmware_params ,
                   isilon_params ,
                   netapp_params ,
                   generic_nas_params ,
                   flashblade_params ,
                   elastifile_params ,
                   gpfs_params ,
                   mssql_params ,
                   oracle_params ,
                   physical_params ,
                   sharepoint_params ,
                   group_params ,
                   uda_params ,
                   view_params ,
                   mongo_db_params)