# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.register_cassandra_source_request_parameters


class SourceRegistrationPatchParameters(object):

    """Implementation of the 'Source Registration update parameters.' model.

    Specifies the Source registration Update request parameters.

    Attributes:
        environment (Environment8Enum): Specifies the environment type of the
            Protection Source.
        cassandra_params (RegisterCassandraSourceRequestParameters): Specifies
            parameters to register cassandra source.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "environment":'environment',
        "cassandra_params":'cassandraParams'
    }

    def __init__(self,
                 environment=None,
                 cassandra_params=None,
               ):
        """Constructor for the SourceRegistrationUpdateParameters class"""

        # Initialize members of the class
        self.environment = environment
        self.cassandra_params = cassandra_params


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
        environment = dictionary.get('environment')
        cassandra_params = cohesity_management_sdk.models_v2.register_cassandra_source_request_parameters.RegisterCassandraSourceRequestParameters.from_dictionary(dictionary.get('cassandraParams')) if dictionary.get('cassandraParams') else None

        # Return an object of this model
        return cls(environment,
                   cassandra_params,
                  )


