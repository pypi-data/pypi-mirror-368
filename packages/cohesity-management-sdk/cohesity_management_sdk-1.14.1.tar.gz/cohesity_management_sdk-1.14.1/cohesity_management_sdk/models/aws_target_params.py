# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.aws_target_params_network_config

class AwsTargetParams(object):

    """Implementation of the 'AwsTargetParams' model.

    TODO: type model description here.

    Attributes:
        custom_server_config (AwsTargetParams_NetworkConfig): Custom
            destination Server configuration parameters where the RDS
            Postgres database will be recovered."
        is_known_source (bool): If set to true means we are recovering to a
            know source and 'known_source_config'' will be populated else
            'custom_server_config' will be populated.
        known_kource_config (AwsTargetParams_NetworkConfig): Populated in
            case of a known target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "custom_server_config":'customServerConfig',
        "is_known_source":'isKnownSource',
        "known_kource_config":'knownSourceConfig'
    }

    def __init__(self,
                 custom_server_config=None,
                 is_known_source=None,
                 known_kource_config=None):
        """Constructor for the AwsTargetParams class"""

        # Initialize members of the class
        self.custom_server_config = custom_server_config
        self.is_known_source = is_known_source
        self.known_kource_config = known_kource_config


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
        custom_server_config = cohesity_management_sdk.models.aws_target_params_network_config.AwsTargetParams_NetworkConfig.from_dictionary(dictionary.get('customServerConfig')) if dictionary.get('customServerConfig') else None
        is_known_source = dictionary.get('isKnownSource')
        known_kource_config = cohesity_management_sdk.models.aws_target_params_network_config.AwsTargetParams_NetworkConfig.from_dictionary(dictionary.get('knownSourceConfig')) if dictionary.get('knownSourceConfig') else None

        # Return an object of this model
        return cls(custom_server_config,
                   is_known_source,
                   known_kource_config)


