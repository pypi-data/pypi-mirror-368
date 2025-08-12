# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recovery_object_identifier
import cohesity_management_sdk.models_v2.credentials

class RecoverRdsPostgresNewSourceConfig(object):

    """Implementation of the 'RecoverRdsPostgresNewSourceConfig' model.

    Specifies the configuration for recovering RDS Postgres instance
      to the known target.

    Attributes:
        ip (string): Specifies the Ip in which to deploy the Rds instance.
        port (long|int): Specifies the port to use to connect to the server.
        region (RecoveryObjectIdentifier): Specifies the region in which to deploy the Rds instance.
        standard_credentials (Credentials): Specifies the standard username and password type of credentials.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "ip":'ip',
        "port":'port',
        "region":'region',
        "standard_credentials":'standardCredentials'
    }

    def __init__(self,
                 ip=None,
                 port=None,
                 region=None,
                 standard_credentials=None):
        """Constructor for the RecoverRdsPostgresNewSourceConfig class"""

        # Initialize members of the class
        self.ip = ip
        self.port = port
        self.region = region
        self.standard_credentials = standard_credentials


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
        ip = dictionary.get('ip')
        port = dictionary.get('port')
        region = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('region')) if dictionary.get('region') else None
        standard_credentials = cohesity_management_sdk.models_v2.credentials.Credentials.from_dictionary(dictionary.get('standardCredentials')) if dictionary.get('standardCredentials') else None

        # Return an object of this model
        return cls(ip,
                   port,
                   region,
                   standard_credentials)