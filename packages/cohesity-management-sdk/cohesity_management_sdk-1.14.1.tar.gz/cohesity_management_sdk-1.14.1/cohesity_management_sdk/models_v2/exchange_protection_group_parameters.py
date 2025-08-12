# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.exchange_protection_group_object_params
import cohesity_management_sdk.models_v2.indexing_policy

class ExchangeProtectionGroupParameters(object):

    """Implementation of the 'Exchange Protection Group Parameters.' model.

    Specifies the parameters which are specific to Exchange related Protection
    Groups.

    Attributes:
        objects (list of ExchangeProtectionGroupObjectParams): Specifies the
            list of object ids to be protected.
        exclude_database_ids (list of long|int): Specifies the list of IDs of
            the databases to not be protected by this Protection Group. This
            can be used to ignore specific databases under Exchange Server/DAG
            which has been included for protection.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        backups_copy_only (bool): Specifies whether the backups should be
            copy-only.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "exclude_database_ids":'excludeDatabaseIds',
        "indexing_policy":'indexingPolicy',
        "backups_copy_only":'backupsCopyOnly'
    }

    def __init__(self,
                 objects=None,
                 exclude_database_ids=None,
                 indexing_policy=None,
                 backups_copy_only=None):
        """Constructor for the ExchangeProtectionGroupParameters class"""

        # Initialize members of the class
        self.objects = objects
        self.exclude_database_ids = exclude_database_ids
        self.indexing_policy = indexing_policy
        self.backups_copy_only = backups_copy_only


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
                objects.append(cohesity_management_sdk.models_v2.exchange_protection_group_object_params.ExchangeProtectionGroupObjectParams.from_dictionary(structure))
        exclude_database_ids = dictionary.get('excludeDatabaseIds')
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        backups_copy_only = dictionary.get('backupsCopyOnly')

        # Return an object of this model
        return cls(objects,
                   exclude_database_ids,
                   indexing_policy,
                   backups_copy_only)


