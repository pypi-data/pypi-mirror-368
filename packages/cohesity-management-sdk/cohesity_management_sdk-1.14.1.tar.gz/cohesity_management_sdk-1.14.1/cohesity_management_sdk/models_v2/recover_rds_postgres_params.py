# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_protection_group_run_params
import cohesity_management_sdk.models_v2.aws_target_params_for_recover_rds_postgres

class RecoverRdsPostgresParams(object):

    """Implementation of the 'RecoverRdsPostgresParams' model.

    Specifies the parameters to recover RDS Postgres.

    Attributes:
        target_environment (string): Specifies the environment of the recovery
            target. The corresponding params below must be filled out.
        prefix (string): Specifies the prefix to be prepended to the object name after
          the recovery.
        suffix (string): Specifies the suffix to be appended to the object name after
          the recovery.
        overwrite_database (bool): Set to true to overwrite an existing object at the destination.
          If set to false, and the same object exists at the destination, then recovery
          will fail for that object.
        aws_target_params (AwsTargetParamsForRecoverRDSPostgres): Specifies the params for recovering to an Aws target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_environment":'targetEnvironment',
        "prefix":'prefix',
        "suffix":'suffix',
        "overwrite_database":'overwriteDatabase',
        "aws_target_params":'awsTargetParams'
    }

    def __init__(self,
                 target_environment='kAWS',
                 prefix=None,
                 suffix=None,
                 overwrite_database=None,
                 aws_target_params=None):
        """Constructor for the RecoverRdsPostgresParams class"""

        # Initialize members of the class
        self.target_environment = target_environment
        self.prefix = prefix
        self.suffix = suffix
        self.overwrite_database = overwrite_database
        self.aws_target_params = aws_target_params


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
        target_environment = dictionary.get("targetEnvironment") if dictionary.get("targetEnvironment") else 'kAWS'
        prefix = dictionary.get('prefix')
        suffix = dictionary.get('suffix')
        overwrite_database = dictionary.get('overwriteDatabase')
        aws_target_params = cohesity_management_sdk.models_v2.aws_target_params_for_recover_rds_postgres.AwsTargetParamsForRecoverRDSPostgres.from_dictionary(dictionary.get('awsTargetParams')) if dictionary.get('awsTargetParams') else None

        # Return an object of this model
        return cls(target_environment,
                   prefix,
                   suffix,
                   overwrite_database,
                   aws_target_params)