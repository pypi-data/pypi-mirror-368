# -*- coding: utf-8 -*-


class RequestParamsToClaimClusterToHelios(object):

    """Implementation of the 'Request params to claim cluster to Helios.' model.

    Specifies the request params to claim clusters to Helios.

    Attributes:
        cluster_id (long|int): Specifies the cluster id.
        cluster_incarnation_id (long|int): Specifies the cluster incarnation
            id.
        cluster_name (string): Specifies the cluster name.
        claim_token (string): Claim token used for authentication.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cluster_id":'clusterId',
        "cluster_incarnation_id":'clusterIncarnationId',
        "cluster_name":'clusterName',
        "claim_token":'claimToken'
    }

    def __init__(self,
                 cluster_id=None,
                 cluster_incarnation_id=None,
                 cluster_name=None,
                 claim_token=None):
        """Constructor for the RequestParamsToClaimClusterToHelios class"""

        # Initialize members of the class
        self.cluster_id = cluster_id
        self.cluster_incarnation_id = cluster_incarnation_id
        self.cluster_name = cluster_name
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
        cluster_id = dictionary.get('clusterId')
        cluster_incarnation_id = dictionary.get('clusterIncarnationId')
        cluster_name = dictionary.get('clusterName')
        claim_token = dictionary.get('claimToken')

        # Return an object of this model
        return cls(cluster_id,
                   cluster_incarnation_id,
                   cluster_name,
                   claim_token)


