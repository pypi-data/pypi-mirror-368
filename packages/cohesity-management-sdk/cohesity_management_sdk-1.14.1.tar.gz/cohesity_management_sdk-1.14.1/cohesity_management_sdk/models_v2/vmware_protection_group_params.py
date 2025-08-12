# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vmware_protection_group_object_params
import cohesity_management_sdk.models_v2.disk_information
import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.pre_and_post_script_params
import cohesity_management_sdk.models_v2.vm_filter
import cohesity_management_sdk.models_v2.vmware_protection_group_standby_resource_params

class VmwareProtectionGroupParams(object):

    """Implementation of the 'VmwareProtectionGroupParams' model.

    Specifies the parameters which are specific to VMware related Protection
    Groups.

    Attributes:
        allow_parallel_runs (bool): Specifies whether or not this job can have parallel runs.
        exclude_filters (list of VMFilter: Specifies the list of exclusion filters applied during the group
          creation or edit. These exclusion filters can be wildcard supported strings
          or regular expressions. Objects satisfying these filters will be excluded
          during backup and also auto protected objects will be ignored if filtered
          by any of the filters.)
        exclude_object_ids (list of long|int): Specifies the list of IDs of the objects to not be protected
          in this backup. This field only applies if provided object id is non leaf
          entity such as Tag or a folder. This can be used to ignore specific objects
          under a parent object which has been included for protection.
        enable_cdp_sync_replication (bool): Specifies whether synchronous replication is enabled for CDP
          Protection Group when replication target is specified in attached policy.
        exclude_vm_tag_ids (list of long|int): Array of Arrays of VM Tag Ids that Specify VMs to Exclude. Optionally
          specify a list of VMs to exclude from protecting by listing Protection Source
          ids of VM Tags in this two dimensional array. Using this two dimensional
          array of Tag ids, the Cluster generates a list of VMs to exclude from protecting,
          which are derived from intersections of the inner arrays and union of the
          outer array, as shown by the following example. For example a Datacenter
          is selected to be protected but you want to exclude all the ''Former Employees''
          VMs in the East and West but keep all the VMs for ''Former Employees'' in
          the South which are also stored in this Datacenter, by specifying the following
          tag id array: [ [1000, 2221], [1000, 3031] ], where 1000 is the ''Former
          Employee'' VM Tag id, 2221 is the ''East'' VM Tag id and 3031 is the ''West''
          VM Tag id. The first inner array [1000, 2221] produces a list of VMs that
          are both tagged with ''Former Employees'' and ''East'' (an intersection).
          The second inner array [1000, 3031] produces a list of VMs that are both
          tagged with ''Former Employees'' and ''West'' (an intersection). The outer
          array combines the list of VMs from the two inner arrays. The list of resulting
          VMs are excluded from being protected this Job.
        leverage_hyperflex_snapshots (bool): Whether to leverage the hyperflex based snapshots for this backup.
          To leverage hyperflex snapshots, it has to first be registered. If hyperflex
          based snapshots cannot be taken, backup will fallback to the default backup
          method.
        leverage_nutanix_snapshots (bool): Whether to leverage the nutanix based snapshots for this backup.
          To leverage nutanix snapshots, it has to first be registered. If nutanix
          based snapshots cannot be taken, backup will fallback to the default backup
          method.
        leverage_storage_snapshots (bool): Whether to leverage the storage array based snapshots for this
          backup. To leverage storage snapshots, the storage array has to be registered
          as a source. If storage based snapshots can not be taken, backup will fallback
          to the default backup method.
        cloud_migration (bool): Specifies whether or not to move the workload to the cloud.
        objects (list of VmwareProtectionGroupObjectParams): Specifies the
            objects to include in this Protection Group.
        global_exclude_disks (list of DiskInformation): Specifies a list of
            disks to exclude from the Protection Group.
            app_consistent_snapshot (bool): Specifies whether or not to quiesce
            apps and the file system in order to take app consistent
            snapshots.
        fallback_to_crash_consistent_snapshot (bool): Specifies whether or not
            to fallback to a crash consistent snapshot in the event that an
            app consistent snapshot fails. This parameter defaults to true and
            only changes the behavior of the operation if
            'appConsistentSnapshot' is set to 'true'.
        skip_physical_rdm_disks (bool): Specifies whether or not to skip
            backing up physical RDM disks. Physical RDM disks cannot be backed
            up, so if you attempt to backup a VM with physical RDM disks and
            this value is set to 'false', then those VM backups will fail.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        pre_post_script (PreAndPostScriptParams): Specifies the params for pre
            and post scripts.
        leverage_san_transport (bool): If this field is set to true, then the
            backup for the objects will be performed using dedicated storage
            area network (SAN) instead of LAN or managment network.
        enable_nbdssl_fallback (bool): If this field is set to true and SAN
            transport backup fails, then backup will fallback to use NBDSSL
            transport. This field only applies if 'leverageSanTransport' is
            set to true.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the objects.
        vm_tag_ids (list of long|int): Array of Array of VM Tag Ids that Specify VMs to Protect. Optionally
          specify a list of VMs to protect by listing Protection Source ids of VM
          Tags in this two dimensional array. Using this two dimensional array of
          Tag ids, the Cluster generates a list of VMs to protect which are derived
          from intersections of the inner arrays and union of the outer array, as
          shown by the following example. To protect only ''Eng'' VMs in the East
          and all the VMs in the West, specify the following tag id array: [ [1101,
          2221], [3031] ], where 1101 is the ''Eng'' VM Tag id, 2221 is the ''East''
          VM Tag id and 3031 is the ''West'' VM Tag id. The inner array [1101, 2221]
          produces a list of VMs that are both tagged with ''Eng'' and ''East'' (an
          intersection). The outer array combines the list from the inner array with
          list of VMs tagged with ''West'' (a union). The list of resulting VMs are
          protected by this Protection Group.
        standby_resource_objects (list of VmwareProtectionGroupStandbyResourceParams):
          Specifies the standby resource objects for this backup.


    """

    # Create a mapping from Model property names to API property names
    _names = {
        "allow_parallel_runs":'allowParallelRuns',
        "exclude_filters":'excludeFilters',
        "exclude_object_ids":'excludeObjectIds',
        "enable_cdp_sync_replication":'enableCdpSyncReplication',
        "exclude_vm_tag_ids":'excludeVmTagIds',
        "leverage_hyperflex_snapshots":'leverageHyperflexSnapshots',
        "leverage_storage_snapshots":'leverageStorageSnapshots',
        "leverage_nutanix_snapshots": 'leverageNutanixSnapshots',
        "cloud_migration":'cloudMigration',
        "objects":'objects',
        "global_exclude_disks":'globalExcludeDisks',
        "app_consistent_snapshot":'appConsistentSnapshot',
        "fallback_to_crash_consistent_snapshot":'fallbackToCrashConsistentSnapshot',
        "skip_physical_rdm_disks":'skipPhysicalRDMDisks',
        "indexing_policy":'indexingPolicy',
        "pre_post_script":'prePostScript',
        "leverage_san_transport":'leverageSanTransport',
        "enable_nbdssl_fallback":'enableNBDSSLFallback',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "vm_tag_ids":'vmTagIds',
        "standby_resource_objects": 'standbyResourceObjects'
    }

    def __init__(self,
                 allow_parallel_runs=None,
                 exclude_filters=None,
                 exclude_object_ids=None,
                 enable_cdp_sync_replication=None,
                 exclude_vm_tag_ids=None,
                 leverage_hyperflex_snapshots=None,
                 leverage_storage_snapshots=None,
                 leverage_nutanix_snapshots=None,
                 cloud_migration=None,
                 objects=None,
                 global_exclude_disks=None,
                 app_consistent_snapshot=None,
                 fallback_to_crash_consistent_snapshot=None,
                 skip_physical_rdm_disks=None,
                 indexing_policy=None,
                 pre_post_script=None,
                 leverage_san_transport=None,
                 enable_nbdssl_fallback=None,
                 source_id=None,
                 source_name=None,
                 vm_tag_ids=None,
                 standby_resource_objects=None):
        """Constructor for the VmwareProtectionGroupParams class"""

        # Initialize members of the class
        self.allow_parallel_runs = allow_parallel_runs
        self.exclude_filters = exclude_filters
        self.exclude_object_ids = exclude_object_ids
        self.enable_cdp_sync_replication = enable_cdp_sync_replication
        self.exclude_vm_tag_ids = exclude_vm_tag_ids
        self.leverage_hyperflex_snapshots = leverage_hyperflex_snapshots
        self.leverage_storage_snapshots = leverage_storage_snapshots
        self.leverage_nutanix_snapshots = leverage_nutanix_snapshots
        self.cloud_migration = cloud_migration
        self.objects = objects
        self.global_exclude_disks = global_exclude_disks
        self.app_consistent_snapshot = app_consistent_snapshot
        self.fallback_to_crash_consistent_snapshot = fallback_to_crash_consistent_snapshot
        self.skip_physical_rdm_disks = skip_physical_rdm_disks
        self.indexing_policy = indexing_policy
        self.pre_post_script = pre_post_script
        self.leverage_san_transport = leverage_san_transport
        self.enable_nbdssl_fallback = enable_nbdssl_fallback
        self.source_id = source_id
        self.source_name = source_name
        self.vm_tag_ids = vm_tag_ids
        self.standby_resource_objects = standby_resource_objects


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
        allow_parallel_runs = dictionary.get('allowParallelRuns')
        exclude_filters = None
        if dictionary.get("excludeFilters") is not None:
            exclude_filters = list()
            for structure in dictionary.get('excludeFilters'):
                exclude_filters.append(cohesity_management_sdk.models_v2.vm_filter.VMFilter.from_dictionary(structure))
        exclude_object_ids = dictionary.get('excludeObjectIds')
        enable_cdp_sync_replication = dictionary.get('enableCdpSyncReplication')
        exclude_vm_tag_ids = dictionary.get('excludeVmTagIds')
        leverage_hyperflex_snapshots = dictionary.get('leverageHyperflexSnapshots')
        leverage_storage_snapshots = dictionary.get('leverageStorageSnapshots')
        leverage_nutanix_snapshots = dictionary.get('leverageNutanixSnapshots')
        cloud_migration = dictionary.get('cloudMigration')
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.vmware_protection_group_object_params.VmwareProtectionGroupObjectParams.from_dictionary(structure))
        global_exclude_disks = None
        if dictionary.get("globalExcludeDisks") is not None:
            global_exclude_disks = list()
            for structure in dictionary.get('globalExcludeDisks'):
                global_exclude_disks.append(cohesity_management_sdk.models_v2.disk_information.DiskInformation.from_dictionary(structure))
        app_consistent_snapshot = dictionary.get('appConsistentSnapshot')
        fallback_to_crash_consistent_snapshot = dictionary.get('fallbackToCrashConsistentSnapshot')
        skip_physical_rdm_disks = dictionary.get('skipPhysicalRDMDisks')
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(
            dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        pre_post_script = cohesity_management_sdk.models_v2.pre_and_post_script_params.PreAndPostScriptParams.from_dictionary(
            dictionary.get('prePostScript')) if dictionary.get('prePostScript') else None
        leverage_san_transport = dictionary.get('leverageSanTransport')
        enable_nbdssl_fallback = dictionary.get('enableNBDSSLFallback')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        vm_tag_ids = dictionary.get('vmTagIds')
        standby_resource_objects = None
        if dictionary.get("standbyResourceObjects") is not None:
            standby_resource_objects = list()
            for structure in dictionary.get('standbyResourceObjects'):
                standby_resource_objects.append(cohesity_management_sdk.models_v2.vmware_protection_group_standby_resource_params.VmwareProtectionGroupStandbyResourceParams.from_dictionary(structure))

        # Return an object of this model
        return cls(allow_parallel_runs,
                   exclude_filters,
                   exclude_object_ids,
                   enable_cdp_sync_replication,
                   exclude_vm_tag_ids,
                   leverage_hyperflex_snapshots,
                   leverage_storage_snapshots,
                   leverage_nutanix_snapshots,
                   cloud_migration,
                   objects,
                   global_exclude_disks,
                   app_consistent_snapshot ,
                   fallback_to_crash_consistent_snapshot ,
                   skip_physical_rdm_disks ,
                   indexing_policy ,
                   pre_post_script ,
                   leverage_san_transport ,
                   enable_nbdssl_fallback,
                   source_id,
                   source_name,
                   vm_tag_ids,
                   standby_resource_objects)