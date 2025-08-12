# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.k_8_s_filter_params

class KubernetesBackupSourceParams(object):

    """Implementation of the 'KubernetesBackupSourceParams' model.

    Message to capture additional backup params for a Kubernetes type
    source.

    Attributes:
        exclude_params (K8SFilterParams): Info about PVC(s) to be excluded from the
            from the backup job for the source. When set, this will override
            KubernetesEnvParams label based PVC filter.
        include_params (K8SFilterParams): Info about PVC(s) to be included from
            the from the backup job for the source. When set, this will override
            KubernetesEnvParams label based PVC filter.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "exclude_params": 'excludeParams',
        "include_params": 'includeParams'
    }

    def __init__(self,
                 exclude_params=None,
                 include_params=None):
        """Constructor for the KubernetesBackupSourceParams class"""

        # Initialize members of the class
        self.exclude_params = exclude_params
        self.include_params = include_params


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
        exclude_params = cohesity_management_sdk.models.k_8_s_filter_params.K8SFilterParams.from_dictionary(dictionary.get('excludeParams', None)) if dictionary.get('excludeParams', None) else None
        include_params = cohesity_management_sdk.models.k_8_s_filter_params.K8SFilterParams.from_dictionary(dictionary.get('includeParams', None)) if dictionary.get('includeParams', None) else None

        # Return an object of this model
        return cls(exclude_params,
                   include_params)


