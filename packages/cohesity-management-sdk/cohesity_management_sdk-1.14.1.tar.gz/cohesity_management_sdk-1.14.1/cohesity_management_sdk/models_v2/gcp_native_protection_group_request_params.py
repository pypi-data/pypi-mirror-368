# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.gcp_native_protection_group_object_params
import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.gcp_disk_exclusion_params

class GCPNativeProtectionGroupRequestParams(object):

    """Implementation of the 'GCP Native Protection Group Request Params.' model.

    Specifies the parameters which are specific to GCP related Protection
    Groups using GCP native snapshot APIs. Atlease one of tags or objects must
    be specified.

    Attributes:
        objects (list of GCPNativeProtectionGroupObjectParams): Specifies the
            objects to be included in the Protection Group.
        exclude_object_ids (list of long|int): Specifies the objects to be
            excluded in the Protection Group.
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
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        gcp_disk_exclusion_params (GcpDiskExclusionParams): Specifies the paramaters to exclude disks attached to GCP VM
          instances.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.
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

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "exclude_object_ids":'excludeObjectIds',
        "exclude_vm_tag_ids":'excludeVmTagIds',
        "indexing_policy":'indexingPolicy',
        "gcp_disk_exclusion_params":'gcpDiskExclusionParams',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "vm_tag_ids":'vmTagIds'
    }

    def __init__(self,
                 objects=None,
                 exclude_object_ids=None,
                 exclude_vm_tag_ids=None,
                 indexing_policy=None,
                 gcp_disk_exclusion_params=None,
                 source_id=None,
                 source_name=None,
                 vm_tag_ids=None):
        """Constructor for the GCPNativeProtectionGroupRequestParams class"""

        # Initialize members of the class
        self.objects = objects
        self.exclude_object_ids = exclude_object_ids
        self.exclude_vm_tag_ids = exclude_vm_tag_ids
        self.indexing_policy = indexing_policy
        self.gcp_disk_exclusion_params = gcp_disk_exclusion_params
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
                objects.append(cohesity_management_sdk.models_v2.gcp_native_protection_group_object_params.GCPNativeProtectionGroupObjectParams.from_dictionary(structure))
        exclude_object_ids = dictionary.get('excludeObjectIds')
        exclude_vm_tag_ids = dictionary.get('excludeVmTagIds')
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        gcp_disk_exclusion_params = cohesity_management_sdk.models_v2.gcp_disk_exclusion_params.GCPDiskExclusionParams.from_dictionary(dictionary.get('gcpDiskExclusionParams')) if dictionary.get('gcpDiskExclusionParams') else None
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        vm_tag_ids = dictionary.get('vmTagIds')

        # Return an object of this model
        return cls(objects,
                   exclude_object_ids,
                   exclude_vm_tag_ids,
                   indexing_policy,
                   gcp_disk_exclusion_params,
                   source_id,
                   source_name,
                    vm_tag_ids)