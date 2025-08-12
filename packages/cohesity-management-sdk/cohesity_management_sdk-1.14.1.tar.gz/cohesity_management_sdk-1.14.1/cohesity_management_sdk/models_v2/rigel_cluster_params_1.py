# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.rigel_cluster_node

class RigelClusterParams1(object):

    """Implementation of the 'Rigel Cluster Params.1' model.

    Params for Rigel Cluster Creation

    Attributes:
        nodes (list of RigelClusterNode): TODO: type description here.
        claim_token (string): Specifies the token which will be used to claim
            this Cluster to Helios.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "nodes":'nodes',
        "claim_token":'claimToken'
    }

    def __init__(self,
                 nodes=None,
                 claim_token=None):
        """Constructor for the RigelClusterParams1 class"""

        # Initialize members of the class
        self.nodes = nodes
        self.claim_token = claim_token


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
        nodes = None
        if dictionary.get("nodes") is not None:
            nodes = list()
            for structure in dictionary.get('nodes'):
                nodes.append(cohesity_management_sdk.models_v2.rigel_cluster_node.RigelClusterNode.from_dictionary(structure))
        claim_token = dictionary.get('claimToken')

        # Return an object of this model
        return cls(nodes,
                   claim_token)


