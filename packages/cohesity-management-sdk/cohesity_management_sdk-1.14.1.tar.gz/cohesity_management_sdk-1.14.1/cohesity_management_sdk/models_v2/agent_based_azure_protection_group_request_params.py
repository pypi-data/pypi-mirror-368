# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.agent_based_azure_protection_group_object_params_has
import cohesity_management_sdk.models_v2.indexing_policy

class AgentBasedAzureProtectionGroupRequestParams(object):

    """Implementation of the 'Agent based Azure Protection Group Request Params.' model.

    Specifies the parameters which are specific to Azure related Protection
    Groups using cohesity protection-service installed on the instance.
    Objects must be specified.

    Attributes:
        objects (list of AgentBasedAzureProtectionGroupObjectParamsHas):
            Specifies the objects to be included in the Protection Group.
        exclude_object_ids (list of long|int): Specifies the objects to be
            excluded in the Protection Group.
        app_consistent_snapshot (bool): Specifies whether or not to quiesce
            apps and the file system in order to take app consistent
            snapshots.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        cloud_migration (bool): Specifies whether or not to move the workload
            to the cloud.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "exclude_object_ids":'excludeObjectIds',
        "app_consistent_snapshot":'appConsistentSnapshot',
        "indexing_policy":'indexingPolicy',
        "cloud_migration":'cloudMigration',
        "source_id":'sourceId',
        "source_name":'sourceName'
    }

    def __init__(self,
                 objects=None,
                 exclude_object_ids=None,
                 app_consistent_snapshot=None,
                 indexing_policy=None,
                 cloud_migration=None,
                 source_id=None,
                 source_name=None):
        """Constructor for the AgentBasedAzureProtectionGroupRequestParams class"""

        # Initialize members of the class
        self.objects = objects
        self.exclude_object_ids = exclude_object_ids
        self.app_consistent_snapshot = app_consistent_snapshot
        self.indexing_policy = indexing_policy
        self.cloud_migration = cloud_migration
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
                objects.append(cohesity_management_sdk.models_v2.agent_based_azure_protection_group_object_params_has.AgentBasedAzureProtectionGroupObjectParamsHas.from_dictionary(structure))
        exclude_object_ids = dictionary.get('excludeObjectIds')
        app_consistent_snapshot = dictionary.get('appConsistentSnapshot')
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        cloud_migration = dictionary.get('cloudMigration')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')

        # Return an object of this model
        return cls(objects,
                   exclude_object_ids,
                   app_consistent_snapshot,
                   indexing_policy,
                   cloud_migration,
                   source_id,
                   source_name)


