# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.targets_configuration

class CascadedTargetConfiguration(object):

    """Implementation of the 'CascadedTargetConfiguration' model.

    Specifies the source of the cascadded replication and list of all
      remote targets that needs to added. Each source cluster and remote targets are
      considered as nodes and immediate connections between them are considered as
      edges.

    Attributes:
        remote_targets (TargetsConfiguration): Specifies the list of remote targets that need to be added from
          the current source.
        source_cluster_id (long|int): Specifies the source cluster id from where the remote operations
          will be performed to the next set of remote targets.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "remote_targets":'remoteTargets',
        "source_cluster_id":'sourceClusterId'
    }

    def __init__(self,
                 remote_targets=None,
                 source_cluster_id=None):
        """Constructor for the CascadedTargetConfiguration class"""

        # Initialize members of the class
        self.remote_targets = remote_targets
        self.source_cluster_id = source_cluster_id



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
        remote_targets = cohesity_management_sdk.models_v2.targets_configuration.TargetsConfiguration.from_dictionary(dictionary.get('remoteTargets')) if dictionary.get('remoteTargets') else None
        source_cluster_id = dictionary.get('sourceClusterId')

        # Return an object of this model
        return cls(remote_targets,
                   source_cluster_id)