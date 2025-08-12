# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.replication_target_configuration_3
import cohesity_management_sdk.models_v2.archival_target_configuration_1
import cohesity_management_sdk.models_v2.replication_target_configuration

class TargetConfiguration(object):

    """Implementation of the 'Target Configuration' model.

    Specifies the replication, archival and cloud spin targets of Protection
      Policy.

    Attributes:
        archivals (list of ArchivalTargetConfiguration1): Specifies a
            list of replication targets configurations.
        cloud_replications (list of ReplicationTargetConfiguration3): Specifies a list of cloud replication targets configurations.
        items:
        replications (list of ReplicationTargetConfiguration1): Specifies a list of replication targets configurations.
        use_policy_defaults (bool): Specifies whether to use default policy settings or not. If specified
          as true then 'replications' and 'arcihvals' should not be specified. In
          case of true value, replicatioan targets congfigured in the policy will
          be added internally.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "replications":'replications',
        "cloud_replications":'cloudReplications',
        "archivals":'archivals',
        "use_policy_defaults":'usePolicyDefaults'
    }

    def __init__(self,
                 replications=None,
                 cloud_replications=None,
                 archivals=None,
                 use_policy_defaults=None):
        """Constructor for the TargetConfiguration class"""

        # Initialize members of the class
        self.replications = replications
        self.cloud_replications = cloud_replications
        self.archivals = archivals
        self.use_policy_defaults = use_policy_defaults



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
        replications = None
        if dictionary.get("replications") is not None:
            replications = list()
            for structure in dictionary.get('replications'):
                replications.append(cohesity_management_sdk.models_v2.replication_target_configuration.ReplicationTargetConfiguration.from_dictionary(structure))
        cloud_replications = None
        if dictionary.get('cloudReplications') is not None:
            cloud_replications = list()
            for structure in dictionary.get('cloudReplications'):
                cloud_replications.append(cohesity_management_sdk.models_v2.replication_target_configuration_3.ReplicationTargetConfiguration3.from_dictionary(structure))
        archivals = None
        if dictionary.get("archivals") is not None:
            archivals = list()
            for structure in dictionary.get('archivals'):
                archivals.append(cohesity_management_sdk.models_v2.archival_target_configuration_1.ArchivalTargetConfiguration1.from_dictionary(structure))
        use_policy_defaults = dictionary.get('usePolicyDefaults')

        # Return an object of this model
        return cls(replications,
                   cloud_replications,
                   archivals,
                   use_policy_defaults)