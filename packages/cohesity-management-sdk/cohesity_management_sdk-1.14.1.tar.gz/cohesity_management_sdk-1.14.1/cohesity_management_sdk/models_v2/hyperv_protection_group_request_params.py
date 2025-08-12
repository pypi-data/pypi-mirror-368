# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.hyperv_protection_group_object_params
import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.hyperv_disk_information

class HypervProtectionGroupRequestParams(object):

    """Implementation of the 'HyperV Protection Group Request Params.' model.

    Specifies the parameters which are specific to HyperV related Protection
    Groups.

    Attributes:
        protection_type (ProtectionType7Enum): Specifies the Protection Group
            type. If not specified, then backup method is auto determined.
            Specifying RCT, will forcibly use RCT backup for all VMs in this
            Protection Group. Available only for VMs with hardware version 8.0
            and above, but is more efficient. Specifying VSS, will forcibly
            use VSS backup for all VMs in this Protection Group. Available for
            VMs with hardware version 5.0 and above but is slower than RCT
            backup.
        objects (list of HypervProtectionGroupObjectParams): Specifies the
            objects to be included in the Protection Group.
        exclude_object_ids (list of long|int): Specifies the list of IDs of
            the objects to not be protected by this Protection Group. This can
            be used to ignore specific objects under a parent object which has
            been included for protection.
        vm_tag_ids (list of long|int): Array of Array of VM Tag Ids that
            Specify VMs to Protect. Optionally specify a list of VMs to
            protect by listing Protection Source ids of VM Tags in this two
            dimensional array. Using this two dimensional array of Tag ids,
            the Cluster generates a list of VMs to protect which are derived
            from intersections of the inner arrays and union of the outer
            array, as shown by the following example. To protect only 'Eng'
            VMs in the East and all the VMs in the West, specify the following
            tag id array: [ [1101, 2221], [3031] ], where 1101 is the 'Eng' VM
            Tag id, 2221 is the 'East' VM Tag id and 3031 is the 'West' VM Tag
            id. The inner array [1101, 2221] produces a list of VMs that are
            both tagged with 'Eng' and 'East' (an intersection). The outer
            array combines the list from the inner array with list of VMs
            tagged with 'West' (a union). The list of resulting VMs are
            protected by this Protection Group.
        exclude_vm_tag_ids (list of long|int): Array of Arrays of VM Tag Ids
            that Specify VMs to Exclude. Optionally specify a list of VMs to
            exclude from protecting by listing Protection Source ids of VM
            Tags in this two dimensional array. Using this two dimensional
            array of Tag ids, the Cluster generates a list of VMs to exclude
            from protecting, which are derived from intersections of the inner
            arrays and union of the outer array, as shown by the following
            example. For example a Datacenter is selected to be protected but
            you want to exclude all the 'Former Employees' VMs in the East and
            West but keep all the VMs for 'Former Employees' in the South
            which are also stored in this Datacenter, by specifying the
            following tag id array: [ [1000, 2221], [1000, 3031] ], where 1000
            is the 'Former Employee' VM Tag id, 2221 is the 'East' VM Tag id
            and 3031 is the 'West' VM Tag id. The first inner array [1000,
            2221] produces a list of VMs that are both tagged with 'Former
            Employees' and 'East' (an intersection). The second inner array
            [1000, 3031] produces a list of VMs that are both tagged with
            'Former Employees' and 'West' (an intersection). The outer array
            combines the list of VMs from the two inner arrays. The list of
            resulting VMs are excluded from being protected this Job.
        global_exclude_disks (list of HyperVDiskInfo): Specifies a global list of disks to be excluded for the all
            the VMs part of the protection group.
        global_include_disks (list of HyperVDiskInfo): SSpecifies a global list of disks to be included for the all
            the VMs part of the protection group.
        app_consistent_snapshot (bool): Specifies whether or not to quiesce
            apps and the file system in order to take app consistent
            snapshots. If not specified or false then snapshots will not be
            app consistent.
        fallback_to_crash_consistent_snapshot (bool): Specifies whether or not
            to fallback to a crash consistent snapshot in the event that an
            app consistent snapshot fails.
        cloud_migration (bool): Specifies whether or not to move the workload
            to the cloud.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_type":'protectionType',
        "objects":'objects',
        "exclude_object_ids":'excludeObjectIds',
        "vm_tag_ids":'vmTagIds',
        "exclude_vm_tag_ids":'excludeVmTagIds',
        "global_exclude_disks":'globalExcludeDisks',
        "global_include_disks":'globalIncludeDisks',
        "app_consistent_snapshot":'appConsistentSnapshot',
        "fallback_to_crash_consistent_snapshot":'fallbackToCrashConsistentSnapshot',
        "cloud_migration":'cloudMigration',
        "indexing_policy":'indexingPolicy',
        "source_id":'sourceId',
        "source_name":'sourceName'
    }

    def __init__(self,
                 protection_type=None,
                 objects=None,
                 exclude_object_ids=None,
                 vm_tag_ids=None,
                 exclude_vm_tag_ids=None,
                 global_exclude_disks=None,
                 global_include_disks=None,
                 app_consistent_snapshot=None,
                 fallback_to_crash_consistent_snapshot=None,
                 cloud_migration=None,
                 indexing_policy=None,
                 source_id=None,
                 source_name=None):
        """Constructor for the HypervProtectionGroupRequestParams class"""

        # Initialize members of the class
        self.protection_type = protection_type
        self.objects = objects
        self.exclude_object_ids = exclude_object_ids
        self.vm_tag_ids = vm_tag_ids
        self.exclude_vm_tag_ids = exclude_vm_tag_ids
        self.global_exclude_disks = global_exclude_disks
        self.global_include_disks = global_include_disks
        self.app_consistent_snapshot = app_consistent_snapshot
        self.fallback_to_crash_consistent_snapshot = fallback_to_crash_consistent_snapshot
        self.cloud_migration = cloud_migration
        self.indexing_policy = indexing_policy
        self.source_id = source_id
        self.source_name = source_name


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
        protection_type = dictionary.get('protectionType')
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.hyperv_protection_group_object_params.HypervProtectionGroupObjectParams.from_dictionary(structure))
        exclude_object_ids = dictionary.get('excludeObjectIds')
        vm_tag_ids = dictionary.get('vmTagIds')
        exclude_vm_tag_ids = dictionary.get('excludeVmTagIds')
        global_exclude_disks = None
        if dictionary.get("globalExcludeDisks") is not None:
            global_exclude_disks = list()
            for structure in dictionary.get('globalExcludeDisks'):
                global_exclude_disks.append(cohesity_management_sdk.models_v2.hyperv_disk_information.HypervDiskInformation.from_dictionary(structure))
        global_include_disks = None
        if dictionary.get("globalIncludeDisks") is not None:
            global_include_disks = list()
            for structure in dictionary.get('globalIncludeDisks'):
                global_include_disks.append(cohesity_management_sdk.models_v2.hyperv_disk_information.HypervDiskInformation.from_dictionary(structure))
        app_consistent_snapshot = dictionary.get('appConsistentSnapshot')
        fallback_to_crash_consistent_snapshot = dictionary.get('fallbackToCrashConsistentSnapshot')
        cloud_migration = dictionary.get('cloudMigration')
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')

        # Return an object of this model
        return cls(protection_type,
                   objects,
                   exclude_object_ids,
                   vm_tag_ids,
                   exclude_vm_tag_ids,
                   global_exclude_disks,
                   global_include_disks,
                   app_consistent_snapshot,
                   fallback_to_crash_consistent_snapshot,
                   cloud_migration,
                   indexing_policy,
                   source_id,
                   source_name)