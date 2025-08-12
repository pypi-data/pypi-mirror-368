# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.aws_entity
import cohesity_management_sdk.models.credentials_proto

class AwsTargetParams_NetworkConfig(object):

    """Implementation of the 'AwsTargetParams_NetworkConfig' model.

    Proto to define the network configuration to be applied to the target
    restore.

    Attributes:
        credentials (CredentialsProto): Postgres Server login credentials.
        instance (AwsEntity): instance in which to deploy the Rds Postgres
            database.
        ip (string): Ip in which to deploy the Rds Postgres database.
        is_new_source (bool): If set to true means we are recovering to the same destination
          where

          the backup is made from. We are not needed to fill any other config if

          this is set to true. Magneto itself will fetch the config in this case.
        port (int): Port to use to connect to the RDS Postgres server.
        region (AwsEntity): Region in which to deploy the Rds Postgres
            database.
        source (AwsEntity): Target source details where RDS Postgres database
            will be recovered.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "credentials": 'credentials',
        "instance": 'instance',
        "ip": 'ip',
        "is_new_source": 'isNewSource',
        "port":'port',
        "region":'region',
        "source":'source'
    }

    def __init__(self,
                 credentials=None,
                 instance=None,
                 ip=None,
                 is_new_source=None,
                 port=None,
                 region=None,
                 source=None):
        """Constructor for the AwsTargetParams_NetworkConfig class"""

        # Initialize members of the class
        self.credentials = credentials
        self.instance = instance
        self.ip = ip
        self.is_new_source = is_new_source
        self.port = port
        self.region = region
        self.source = source

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
        credentials = cohesity_management_sdk.models.credentials_proto.CredentialsProto.from_dictionary(dictionary.get('credentials')) if dictionary.get('credentials') else None
        instance = cohesity_management_sdk.models.aws_entity.AwsEntity.from_dictionary(dictionary.get('instance')) if dictionary.get('instance') else None
        ip = dictionary.get('ip')
        is_new_source = dictionary.get('isNewSource')
        port = dictionary.get('port')
        region = cohesity_management_sdk.models.aws_entity.AwsEntity.from_dictionary(dictionary.get('region')) if dictionary.get('region') else None
        source = cohesity_management_sdk.models.aws_entity.AwsEntity.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None

        # Return an object of this model
        return cls(credentials,
                   instance,
                   ip,
                   is_new_source,
                   port,
                   region,
                   source)


