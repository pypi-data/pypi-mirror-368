# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_rds_postgres_known_source_config
import cohesity_management_sdk.models_v2.recover_rds_postgres_new_source_config

class AwsTargetParamsForRecoverRDSPostgres(object):

    """Implementation of the 'AwsTargetParamsForRecoverRDSPostgres' model.

    Specifies the recovery target params for RDS Postgres target config.

    Attributes:
        custom_server_config (RecoverRdsPostgresNewSourceConfig): Specifies the custom destination Server configuration parameters
          where the RDS Postgres instances will be recovered.
        known_source_config (RecoverRdsPostgresKnownSourceConfig): Specifies the destination Source configuration parameters where
          the RDS Postgres instances will be recovered. This is mandatory if recoverToKnownSource
          is set to true.
        recover_to_known_source (bool): Specifies whether the recovery should be performed to a known
          or a custom target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "custom_server_config":'customServerConfig',
        "known_source_config":'knownSourceConfig',
        "recover_to_known_source":'recoverToKnownSource'
    }

    def __init__(self,
                 custom_server_config=None,
                 known_source_config=None,
                 recover_to_known_source=None):
        """Constructor for the AwsTargetParamsForRecoverRDSPostgres class"""

        # Initialize members of the class
        self.custom_server_config = custom_server_config
        self.known_source_config = known_source_config
        self.recover_to_known_source = recover_to_known_source


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
        custom_server_config = cohesity_management_sdk.models_v2.recover_rds_postgres_new_source_config.RecoverRdsPostgresNewSourceConfig.from_dictionary(
            dictionary.get('customServerConfig')) if dictionary.get('customServerConfig') else None
        known_source_config = cohesity_management_sdk.models_v2.recover_rds_postgres_known_source_config.RecoverRdsPostgresKnownSourceConfig.from_dictionary(
            dictionary.get('knownSourceConfig')) if dictionary.get('knownSourceConfig') else None
        recover_to_known_source = dictionary.get('recoverToKnownSource')

        # Return an object of this model
        return cls(custom_server_config,
                   known_source_config,
                   recover_to_known_source)