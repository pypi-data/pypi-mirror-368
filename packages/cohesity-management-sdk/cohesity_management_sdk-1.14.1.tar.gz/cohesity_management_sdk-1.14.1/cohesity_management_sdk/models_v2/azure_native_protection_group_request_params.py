# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.azure_native_protection_group_object_params
import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.cloud_pre_post_backup_scripts
import cohesity_management_sdk.models_v2.data_transfer_info_request

class AzureNativeProtectionGroupRequestParams(object):

    """Implementation of the 'Azure Native Protection Group Request Params.' model.

    Specifies the parameters which are specific to Azure related Protection
    Groups using Azure native snapshot APIs. Objects must be specified.

    Attributes:
        objects (list of AzureNativeProtectionGroupObjectParams): Specifies
            the objects to be included in the Protection Group.
        exclude_object_ids (list of long|int): Specifies the objects to be
            excluded in the Protection Group.
        exclude_vm_tag_ids (list of long|int): Array of arrays of VM Tag Ids that Specify VMs to Exclude.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        cloud_migration (bool): Specifies whether or not to move the workload
            to the cloud.
        cloud_pre_post_script (CloudBackupScriptParams): Specifies the pre script and post script to run before and after
          the backup.
        data_transfer_info (DataTransferInfo): Specifies the the details of network used in transferring the
          data from source account to Cohesity cluste
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.
        vm_tag_ids (list of long|int): Array of arrays of VM Tag Ids that Specify VMs to Protect.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "exclude_object_ids":'excludeObjectIds',
        "exclude_vm_tag_ids":'excludeVmTagIds',
        "indexing_policy":'indexingPolicy',
        "cloud_migration":'cloudMigration',
        "cloud_pre_post_script":'cloudPrePostScript',
        "data_transfer_info":'dataTransferInfo',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "vm_tag_ids":'vmTagIds'
    }

    def __init__(self,
                 objects=None,
                 exclude_object_ids=None,
                 exclude_vm_tag_ids=None,
                 indexing_policy=None,
                 cloud_migration=None,
                 cloud_pre_post_script=None,
                 data_transfer_info=None,
                 source_id=None,
                 source_name=None,
                 vm_tag_ids=None):
        """Constructor for the AzureNativeProtectionGroupRequestParams class"""

        # Initialize members of the class
        self.objects = objects
        self.exclude_object_ids = exclude_object_ids
        self.exclude_vm_tag_ids = exclude_vm_tag_ids
        self.indexing_policy = indexing_policy
        self.cloud_migration = cloud_migration
        self.cloud_pre_post_script = cloud_pre_post_script
        self.data_transfer_info = data_transfer_info
        self.source_id = source_id
        self.source_name = source_name
        self.vm_tag_ids = vm_tag_ids


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
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.azure_native_protection_group_object_params.AzureNativeProtectionGroupObjectParams.from_dictionary(structure))
        exclude_object_ids = dictionary.get('excludeObjectIds')
        exclude_vm_tag_ids = dictionary.get('excludeVmTagIds')
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        cloud_migration = dictionary.get('cloudMigration')
        cloud_pre_post_script = cohesity_management_sdk.models_v2.cloud_pre_post_backup_scripts.CloudPrePostBackupScripts.from_dictionary(dictionary.get('cloudPrePostScript')) if dictionary.get('cloudPrePostScript') else None
        data_transfer_info = cohesity_management_sdk.models_v2.data_transfer_info_request.DataTransferInfoRequest.from_dictionary(dictionary.get('dataTransferInfo')) if dictionary.get('dataTransferInfo') else None
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        vm_tag_ids = dictionary.get('vmTagIds')

        # Return an object of this model
        return cls(objects,
                   exclude_object_ids,
                   exclude_vm_tag_ids,
                   indexing_policy,
                   cloud_migration,
                   cloud_pre_post_script,
                   data_transfer_info,
                   source_id,
                   source_name,
                   vm_tag_ids)