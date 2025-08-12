# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.azure_snapshot_manager_protection_group_object_params
import cohesity_management_sdk.models_v2.cloud_pre_post_backup_scripts

class CreateAzureSnapshotManagerProtectionGroupRequestBody(object):

    """Implementation of the 'Create Azure Snapshot Manager Protection Group Request Body' model.

    Specifies the parameters which are specific to Azure related Protection
    Groups using Azure native snapshot orchestration with snapshot manager.
    Objects must be specified.

    Attributes:
        cloud_pre_post_script (CloudBackupScriptParams): Specifies the pre script and post script to run before and after
          the backup.
        objects (list of AzureSnapshotManagerProtectionGroupObjectParams):
            Specifies the objects to be included in the Protection Group.
        exclude_object_ids (list of long|int): Specifies the objects to be
            excluded in the Protection Group.
        exclude_vm_tag_ids (list of long|int): Array of arrays of VM Tag Ids that Specify VMs to Exclude.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.
        vm_tag_ids (list of long|int): Array of arrays of VM Tag Ids that Specify VMs to Protect.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cloud_pre_post_script":'cloudPrePostScript',
        "objects":'objects',
        "exclude_object_ids":'excludeObjectIds',
        "exclude_vm_tag_ids":'excludeVmTagIds',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "vm_tag_ids":'vmTagIds'
    }

    def __init__(self,
                 cloud_pre_post_script=None,
                 objects=None,
                 exclude_object_ids=None,
                 exclude_vm_tag_ids=None,
                 source_id=None,
                 source_name=None,
                 vm_tag_ids=None):
        """Constructor for the CreateAzureSnapshotManagerProtectionGroupRequestBody class"""

        # Initialize members of the class
        self.cloud_pre_post_script = cloud_pre_post_script
        self.objects = objects
        self.exclude_object_ids = exclude_object_ids
        self.exclude_vm_tag_ids = exclude_vm_tag_ids
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
        cloud_pre_post_script = cohesity_management_sdk.models_v2.cloud_pre_post_backup_scripts.CloudPrePostBackupScripts.from_dictionary(dictionary.get('cloudPrePostScript')) if dictionary.get('cloudPrePostScript') else None
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.azure_snapshot_manager_protection_group_object_params.AzureSnapshotManagerProtectionGroupObjectParams.from_dictionary(structure))
        exclude_object_ids = dictionary.get('excludeObjectIds')
        exclude_vm_tag_ids = dictionary.get('excludeVmTagIds')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        vm_tag_ids = dictionary.get('vmTagIds')

        # Return an object of this model
        return cls(cloud_pre_post_script,
                   objects,
                   exclude_object_ids,
                   exclude_vm_tag_ids,
                   source_id,
                   source_name,
                   vm_tag_ids)