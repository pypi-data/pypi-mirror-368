# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_protection_stats_summary
import cohesity_management_sdk.models_v2.permissions_information
import cohesity_management_sdk.models_v2.vmware_object_entity_params
import cohesity_management_sdk.models_v2.isilon_params_1
import cohesity_management_sdk.models_v2.netapp_params_1
import cohesity_management_sdk.models_v2.generic_nas_params_1
import cohesity_management_sdk.models_v2.flashblade_params_2
import cohesity_management_sdk.models_v2.elastifile_params_1
import cohesity_management_sdk.models_v2.gpfs_params_1
import cohesity_management_sdk.models_v2.object_information_1

class ObjectInformation1(object):

    """Implementation of the 'Object information1' model.

    Specifies information of the object and its children objects.

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
        protection_stats (list of ObjectProtectionStatsSummary): Specifies the
            count and size of protected and unprotected objects for the size.
        permissions (PermissionsInformation): Specifies the list of users,
            groups and users that have permissions for a given object.
        vmware_params (VmwareObjectEntityParams): Object details for Vmware.
        isilon_params (IsilonParams1): Specifies the parameters for Isilon
            object.
        netapp_params (NetappParams1): Specifies the parameters for NetApp
            object.
        generic_nas_params (GenericNasParams1): Specifies the parameters for
            GenericNas object.
        flashblade_params (FlashbladeParams2): Specifies the parameters for
            Flashblade object.
        elastifile_params (ElastifileParams1): Specifies the parameters for
            Elastifile object.
        gpfs_params (GpfsParams1): Specifies the parameters for GPFS object.
        objects (list of ObjectInformation1): Specifies a list of child nodes
            for this specific node.

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
        "protection_stats":'protectionStats',
        "permissions":'permissions',
        "vmware_params":'vmwareParams',
        "isilon_params":'isilonParams',
        "netapp_params":'netappParams',
        "generic_nas_params":'genericNasParams',
        "flashblade_params":'flashbladeParams',
        "elastifile_params":'elastifileParams',
        "gpfs_params":'gpfsParams',
        "objects":'objects'
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
                 protection_stats=None,
                 permissions=None,
                 vmware_params=None,
                 isilon_params=None,
                 netapp_params=None,
                 generic_nas_params=None,
                 flashblade_params=None,
                 elastifile_params=None,
                 gpfs_params=None,
                 objects=None):
        """Constructor for the ObjectInformation1 class"""

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
        self.protection_stats = protection_stats
        self.permissions = permissions
        self.vmware_params = vmware_params
        self.isilon_params = isilon_params
        self.netapp_params = netapp_params
        self.generic_nas_params = generic_nas_params
        self.flashblade_params = flashblade_params
        self.elastifile_params = elastifile_params
        self.gpfs_params = gpfs_params
        self.objects = objects


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
        protection_stats = None
        if dictionary.get("protectionStats") is not None:
            protection_stats = list()
            for structure in dictionary.get('protectionStats'):
                protection_stats.append(cohesity_management_sdk.models_v2.object_protection_stats_summary.ObjectProtectionStatsSummary.from_dictionary(structure))
        permissions = cohesity_management_sdk.models_v2.permissions_information.PermissionsInformation.from_dictionary(dictionary.get('permissions')) if dictionary.get('permissions') else None
        vmware_params = cohesity_management_sdk.models_v2.vmware_object_entity_params.VmwareObjectEntityParams.from_dictionary(dictionary.get('vmwareParams')) if dictionary.get('vmwareParams') else None
        isilon_params = cohesity_management_sdk.models_v2.isilon_params_1.IsilonParams1.from_dictionary(dictionary.get('isilonParams')) if dictionary.get('isilonParams') else None
        netapp_params = cohesity_management_sdk.models_v2.netapp_params_1.NetappParams1.from_dictionary(dictionary.get('netappParams')) if dictionary.get('netappParams') else None
        generic_nas_params = cohesity_management_sdk.models_v2.generic_nas_params_1.GenericNasParams1.from_dictionary(dictionary.get('genericNasParams')) if dictionary.get('genericNasParams') else None
        flashblade_params = cohesity_management_sdk.models_v2.flashblade_params_2.FlashbladeParams2.from_dictionary(dictionary.get('flashbladeParams')) if dictionary.get('flashbladeParams') else None
        elastifile_params = cohesity_management_sdk.models_v2.elastifile_params_1.ElastifileParams1.from_dictionary(dictionary.get('elastifileParams')) if dictionary.get('elastifileParams') else None
        gpfs_params = cohesity_management_sdk.models_v2.gpfs_params_1.GpfsParams1.from_dictionary(dictionary.get('gpfsParams')) if dictionary.get('gpfsParams') else None
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.object_information_1.ObjectInformation1.from_dictionary(structure))

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
                   protection_stats,
                   permissions,
                   vmware_params,
                   isilon_params,
                   netapp_params,
                   generic_nas_params,
                   flashblade_params,
                   elastifile_params,
                   gpfs_params,
                   objects)