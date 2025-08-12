# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.aws_native_protection_group_object_params
import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.ebs_volume_exclusion_params

class AWSNativeProtectionGroupRequestParams(object):

    """Implementation of the 'AWS Native Protection Group Request Params.' model.

    Specifies the parameters which are specific to AWS related Protection
    Groups using AWS native snapshot APIs. Atlease one of tags or objects must
    be specified.

    Attributes:
        objects (list of AWSNativeProtectionGroupObjectParams): Specifies the
            objects to be included in the Protection Group.
        exclude_object_ids (list of long|int): Specifies the objects to be
            excluded in the Protection Group.
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
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        volume_exclusion_params (EbsVolumeExclusionParams): Specifies the paramaters to exclude volumes attached to EC2 instances
          at global level.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "exclude_object_ids":'excludeObjectIds',
        "vm_tag_ids":'vmTagIds',
        "exclude_vm_tag_ids":'excludeVmTagIds',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "indexing_policy":'indexingPolicy',
        "volume_exclusion_params":'volumeExclusionParams'
    }

    def __init__(self,
                 objects=None,
                 exclude_object_ids=None,
                 vm_tag_ids=None,
                 exclude_vm_tag_ids=None,
                 source_id=None,
                 source_name=None,
                 indexing_policy=None,
                 volume_exclusion_params=None):
        """Constructor for the AWSNativeProtectionGroupRequestParams class"""

        # Initialize members of the class
        self.objects = objects
        self.exclude_object_ids = exclude_object_ids
        self.vm_tag_ids = vm_tag_ids
        self.exclude_vm_tag_ids = exclude_vm_tag_ids
        self.source_id = source_id
        self.source_name = source_name
        self.indexing_policy = indexing_policy
        self.volume_exclusion_params = volume_exclusion_params


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
                objects.append(cohesity_management_sdk.models_v2.aws_native_protection_group_object_params.AWSNativeProtectionGroupObjectParams.from_dictionary(structure))
        exclude_object_ids = dictionary.get('excludeObjectIds')
        vm_tag_ids = dictionary.get('vmTagIds')
        exclude_vm_tag_ids = dictionary.get('excludeVmTagIds')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        volume_exclusion_params = cohesity_management_sdk.models_v2.ebs_volume_exclusion_params.EBSVolumeExclusionParams.from_dictionary(dictionary.get('volumeExclusionParams')) if dictionary.get('volumeExclusionParams') else None

        # Return an object of this model
        return cls(objects,
                   exclude_object_ids,
                   vm_tag_ids,
                   exclude_vm_tag_ids,
                   source_id,
                   source_name,
                   indexing_policy,
                   volume_exclusion_params)