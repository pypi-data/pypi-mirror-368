# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.aws_target_params


class RestoreRDSPostgresParams(object):

    """Implementation of the 'RestoreRDSPostgresParams' model.

    Attributes:
        aws_target_params (AwsTargetParams): Target Parameters to be filled if
            Restore target is AWS.
        overwrite_database (bool): If false, recovery will fail if the database
            (with same name as this request) exists on the target server.
            If true, recovery will delete/overwrite the existing database as
            part of recovery.
        prefix_to_database_name (string): Specifies the prefix to be prepended
            to the object name after the recovery.
        suffix_to_database_name (string): Specifies the suffix to be appended
            to the object name after the recovery

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "aws_target_params":'awsTargetParams',
        "overwrite_database":'overwriteDatabase',
        "prefix_to_database_name":'prefixToDatabaseName',
        "suffix_to_database_name":'suffixToDatabaseName'
    }

    def __init__(self,
                 aws_target_params=None,
                 overwrite_database=None,
                 prefix_to_database_name=None,
                 suffix_to_database_name=None):
        """Constructor for the RestoreRDSPostgresParams class"""

        # Initialize members of the class
        self.aws_target_params = aws_target_params
        self.overwrite_database = overwrite_database
        self.prefix_to_database_name = prefix_to_database_name
        self.suffix_to_database_name = suffix_to_database_name


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
        aws_target_params = cohesity_management_sdk.models.aws_target_params.AwsTargetParams.from_dictionary(dictionary.get('awsTargetParams')) if dictionary.get('awsTargetParams') else None
        overwrite_database = dictionary.get('overwriteDatabase')
        prefix_to_database_name = dictionary.get('prefixToDatabaseName')
        suffix_to_database_name = dictionary.get('suffixToDatabaseName')

        # Return an object of this model
        return cls(aws_target_params,
                   overwrite_database,
                   prefix_to_database_name,
                   suffix_to_database_name)


