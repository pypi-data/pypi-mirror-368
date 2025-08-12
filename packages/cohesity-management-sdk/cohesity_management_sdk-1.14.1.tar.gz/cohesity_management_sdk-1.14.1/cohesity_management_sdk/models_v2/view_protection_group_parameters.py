# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.view_protection_group_object_params
import cohesity_management_sdk.models_v2.replication_parameters_1
import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.externally_triggered_job_params

class ViewProtectionGroupParameters(object):

    """Implementation of the 'View Protection Group Parameters' model.

    Specifies the parameters which are specific to view related Protection
    Groups.

    Attributes:
        objects (list of ViewProtectionGroupObjectParams): Specifies the
            objects to be included in the Protection Group.
        replication_params (ReplicationParameters1): Specifies the parameters
            for view replication.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        externally_triggered_job_params (ExternallyTriggeredJobParams):
            Specifies the externally triggered job paramters.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "replication_params":'replicationParams',
        "indexing_policy":'indexingPolicy',
        "externally_triggered_job_params":'externallyTriggeredJobParams'
    }

    def __init__(self,
                 objects=None,
                 replication_params=None,
                 indexing_policy=None,
                 externally_triggered_job_params=None):
        """Constructor for the ViewProtectionGroupParameters class"""

        # Initialize members of the class
        self.objects = objects
        self.replication_params = replication_params
        self.indexing_policy = indexing_policy
        self.externally_triggered_job_params = externally_triggered_job_params


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
                objects.append(cohesity_management_sdk.models_v2.view_protection_group_object_params.ViewProtectionGroupObjectParams.from_dictionary(structure))
        replication_params = cohesity_management_sdk.models_v2.replication_parameters_1.ReplicationParameters1.from_dictionary(dictionary.get('replicationParams')) if dictionary.get('replicationParams') else None
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        externally_triggered_job_params = cohesity_management_sdk.models_v2.externally_triggered_job_params.ExternallyTriggeredJobParams.from_dictionary(dictionary.get('externallyTriggeredJobParams')) if dictionary.get('externallyTriggeredJobParams') else None

        # Return an object of this model
        return cls(objects,
                   replication_params,
                   indexing_policy,
                   externally_triggered_job_params)