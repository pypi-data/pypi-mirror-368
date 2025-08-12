# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.filter

class VmwareProtectionGroupExtraParams(object):

    """Implementation of the 'VmwareProtectionGroupExtraParams' model.

    Specifies the extra parameters which are specific to VMware object
    protection Group.

    Attributes:
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.
        exclude_object_ids (list of long|int): Specifies the list of IDs of
            the objects to not be protected in this backup. This field only
            applies if provided object id is non leaf entity such as Tag or a
            folder. This can be used to ignore specific objects under a parent
            object which has been included for protection.
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
        exclude_filters (list of Filter): Specifies the list of exclusion
            filters applied during the group creation or edit. These exclusion
            filters can be wildcard supported strings or regular expressions.
            Objects satisfying these filters will be excluded during backup
            and also auto protected objects will be ignored if filtered by any
            of the filters.
        leverage_storage_snapshots (bool): Whether to leverage the storage
            array based snapshots for this backup. To leverage storage
            snapshots, the storage array has to be registered as a source. If
            storage based snapshots can not be taken, backup will fallback to
            the default backup method.
        leverage_hyperflex_snapshots (bool): Whether to leverage the hyperflex
            based snapshots for this backup. To leverage hyperflex snapshots,
            it has to first be registered. If hyperflex based snapshots cannot
            be taken, backup will fallback to the default backup method.
        leverage_nutanix_snapshots (bool): Whether to leverage the nutanix
            based snapshots for this backup. To leverage nutanix snapshots, it
            has to first be registered. If nutanix based snapshots cannot be
            taken, backup will fallback to the default backup method.
        cloud_migration (bool): Specifies whether or not to move the workload
            to the cloud.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_id":'sourceId',
        "source_name":'sourceName',
        "exclude_object_ids":'excludeObjectIds',
        "vm_tag_ids":'vmTagIds',
        "exclude_vm_tag_ids":'excludeVmTagIds',
        "exclude_filters":'excludeFilters',
        "leverage_storage_snapshots":'leverageStorageSnapshots',
        "leverage_hyperflex_snapshots":'leverageHyperflexSnapshots',
        "leverage_nutanix_snapshots":'leverageNutanixSnapshots',
        "cloud_migration":'cloudMigration'
    }

    def __init__(self,
                 source_id=None,
                 source_name=None,
                 exclude_object_ids=None,
                 vm_tag_ids=None,
                 exclude_vm_tag_ids=None,
                 exclude_filters=None,
                 leverage_storage_snapshots=None,
                 leverage_hyperflex_snapshots=None,
                 leverage_nutanix_snapshots=None,
                 cloud_migration=None):
        """Constructor for the VmwareProtectionGroupExtraParams class"""

        # Initialize members of the class
        self.source_id = source_id
        self.source_name = source_name
        self.exclude_object_ids = exclude_object_ids
        self.vm_tag_ids = vm_tag_ids
        self.exclude_vm_tag_ids = exclude_vm_tag_ids
        self.exclude_filters = exclude_filters
        self.leverage_storage_snapshots = leverage_storage_snapshots
        self.leverage_hyperflex_snapshots = leverage_hyperflex_snapshots
        self.leverage_nutanix_snapshots = leverage_nutanix_snapshots
        self.cloud_migration = cloud_migration


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
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        exclude_object_ids = dictionary.get('excludeObjectIds')
        vm_tag_ids = dictionary.get('vmTagIds')
        exclude_vm_tag_ids = dictionary.get('excludeVmTagIds')
        exclude_filters = None
        if dictionary.get("excludeFilters") is not None:
            exclude_filters = list()
            for structure in dictionary.get('excludeFilters'):
                exclude_filters.append(cohesity_management_sdk.models_v2.filter.Filter.from_dictionary(structure))
        leverage_storage_snapshots = dictionary.get('leverageStorageSnapshots')
        leverage_hyperflex_snapshots = dictionary.get('leverageHyperflexSnapshots')
        leverage_nutanix_snapshots = dictionary.get('leverageNutanixSnapshots')
        cloud_migration = dictionary.get('cloudMigration')

        # Return an object of this model
        return cls(source_id,
                   source_name,
                   exclude_object_ids,
                   vm_tag_ids,
                   exclude_vm_tag_ids,
                   exclude_filters,
                   leverage_storage_snapshots,
                   leverage_hyperflex_snapshots,
                   leverage_nutanix_snapshots,
                   cloud_migration)


