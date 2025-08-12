# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.response_of_claiming_a_rigel_to_helios
import cohesity_management_sdk.models_v2.response_of_claiming_a_cluster_to_helios

class ResponseOfClaimingAnEntityToHelios(object):

    """Implementation of the 'Response of claiming an entity to Helios.' model.

    Specifies the response of claiming an entity to Helios.

    Attributes:
        entity_type (EntityType1Enum): Specfies the type of entity.
        rigel_params (ResponseOfClaimingARigelToHelios): Specifies the
            response of claiming a Rigel to Helios.
        cluster_params (ResponseOfClaimingAClusterToHelios): Specifies the
            response of claiming a cluster to Helios.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "entity_type":'entityType',
        "rigel_params":'rigelParams',
        "cluster_params":'clusterParams'
    }

    def __init__(self,
                 entity_type=None,
                 rigel_params=None,
                 cluster_params=None):
        """Constructor for the ResponseOfClaimingAnEntityToHelios class"""

        # Initialize members of the class
        self.entity_type = entity_type
        self.rigel_params = rigel_params
        self.cluster_params = cluster_params


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
        entity_type = dictionary.get('entityType')
        rigel_params = cohesity_management_sdk.models_v2.response_of_claiming_a_rigel_to_helios.ResponseOfClaimingARigelToHelios.from_dictionary(dictionary.get('rigelParams')) if dictionary.get('rigelParams') else None
        cluster_params = cohesity_management_sdk.models_v2.response_of_claiming_a_cluster_to_helios.ResponseOfClaimingAClusterToHelios.from_dictionary(dictionary.get('clusterParams')) if dictionary.get('clusterParams') else None

        # Return an object of this model
        return cls(entity_type,
                   rigel_params,
                   cluster_params)


