# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.credentials
import cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration

class ElastifileProtectionSource(object):

    """Implementation of the 'Elastifile Protection Source.' model.

    Specifies parameters to register an Elastifile Source.

    Attributes:
        endpoint (string): Specifies the Hostname or IP Address Endpoint for
            the Elastifile Source.
        credentials (Credentials): Specifies the object to hold username and
            password.
        throttling_config (NasSourceAndProtectionThrottlingConfiguration):
            Specifies the source throttling parameters to be used during full
            or incremental backup of the NAS source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "endpoint":'endpoint',
        "credentials":'credentials',
        "throttling_config":'throttlingConfig'
    }

    def __init__(self,
                 endpoint=None,
                 credentials=None,
                 throttling_config=None):
        """Constructor for the ElastifileProtectionSource class"""

        # Initialize members of the class
        self.endpoint = endpoint
        self.credentials = credentials
        self.throttling_config = throttling_config


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
        endpoint = dictionary.get('endpoint')
        credentials = cohesity_management_sdk.models_v2.credentials.Credentials.from_dictionary(dictionary.get('credentials')) if dictionary.get('credentials') else None
        throttling_config = cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration.NasSourceAndProtectionThrottlingConfiguration.from_dictionary(dictionary.get('throttlingConfig')) if dictionary.get('throttlingConfig') else None

        # Return an object of this model
        return cls(endpoint,
                   credentials,
                   throttling_config)


