# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.awsrds_snapshot_manager_protection_group_object_params

class AWSRDSSnapshotManagerProtectionGroupRequestParams(object):

    """Implementation of the 'AWS RDS Snapshot Manager Protection Group Request Params.' model.

    Specifies the parameters which are specific to AWS RDS related Protection
    Groups.

    Attributes:
        exclude_object_ids (long|int): Specifies the objects to be excluded in the Protection Group.
        exclude_rds_tag_ids (list of long|int): Array of arrays of RDS Tag Ids that Specify db instaces to Exclude.
        objects (list of AWSRDSSnapshotManagerProtectionGroupObjectParams):
            Specifies the objects to be included in the Protection Group.
        rds_tag_ids (list of long|int): Array of arrays of RDS Tag Ids that Specify db instaces to Protect.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "exclude_object_ids":'excludeObjectIds',
        "exclude_rds_tag_ids":'excludeRdsTagIds',
        "objects":'objects',
        "rds_tag_ids":'rdsTagIds',
        "source_id":'sourceId',
        "source_name":'sourceName'
    }

    def __init__(self,
                 exclude_object_ids=None ,
                 exclude_rds_tag_ids=None,
                 objects=None,
                 rds_tag_ids=None,
                 source_id=None,
                 source_name=None):
        """Constructor for the AWSRDSSnapshotManagerProtectionGroupRequestParams class"""

        # Initialize members of the class
        self.exclude_object_ids = exclude_object_ids
        self.exclude_rds_tag_ids = exclude_rds_tag_ids
        self.objects = objects
        self.rds_tag_ids = rds_tag_ids
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
        exclude_object_ids = dictionary.get('excludeObjectIds')
        exclude_rds_tag_ids = dictionary.get('excludeRdsTagIds')
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.awsrds_snapshot_manager_protection_group_object_params.AWSRDSSnapshotManagerProtectionGroupObjectParams.from_dictionary(structure))
        rds_tag_ids = dictionary.get('rdsTagIds')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')

        # Return an object of this model
        return cls(
                   exclude_object_ids,
                   exclude_rds_tag_ids,
                   objects,
                   rds_tag_ids,
                   source_id,
                   source_name)