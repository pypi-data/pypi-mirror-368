# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.aws_aurora_snapshot_manager_protection_group_object_params

class AWSAuroraSnapshotManagerProtectionGroupRequestParams(object):

    """Implementation of the 'AWS Aurora Snapshot Manager Protection Group Request Params.' model.

    Specifies the parameters which are specific to AWS Aurora related
    Protection Groups.

    Attributes:
        objects (list of AWSAuroraSnapshotManagerProtectionGroupObjectParams):
            Specifies the objects to be included in the Protection Group.
        exclude_object_ids (list of long|int): Specifies the objects to be
            excluded in the Protection Group.
        aurora_tag_ids (list of long|int): Array of arrays of Aurora Tag Ids
            that specify aurora clusters to protect.
        exclude_aurora_tag_ids (list of long|int): Array of arrays of RDS Tag
            Ids that specify aurora clusters to exclude.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "exclude_object_ids":'excludeObjectIds',
        "aurora_tag_ids":'auroraTagIds',
        "exclude_aurora_tag_ids":'excludeAuroraTagIds',
        "source_id":'sourceId',
        "source_name":'sourceName'
    }

    def __init__(self,
                 objects=None,
                 exclude_object_ids=None,
                 aurora_tag_ids=None,
                 exclude_aurora_tag_ids=None,
                 source_id=None,
                 source_name=None):
        """Constructor for the AWSAuroraSnapshotManagerProtectionGroupRequestParams class"""

        # Initialize members of the class
        self.objects = objects
        self.exclude_object_ids = exclude_object_ids
        self.aurora_tag_ids = aurora_tag_ids
        self.exclude_aurora_tag_ids = exclude_aurora_tag_ids
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
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.aws_aurora_snapshot_manager_protection_group_object_params.AWSAuroraSnapshotManagerProtectionGroupObjectParams.from_dictionary(structure))
        exclude_object_ids = dictionary.get('excludeObjectIds')
        aurora_tag_ids = dictionary.get('auroraTagIds')
        exclude_aurora_tag_ids = dictionary.get('excludeAuroraTagIds')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')

        # Return an object of this model
        return cls(objects,
                   exclude_object_ids,
                   aurora_tag_ids,
                   exclude_aurora_tag_ids,
                   source_id,
                   source_name)


