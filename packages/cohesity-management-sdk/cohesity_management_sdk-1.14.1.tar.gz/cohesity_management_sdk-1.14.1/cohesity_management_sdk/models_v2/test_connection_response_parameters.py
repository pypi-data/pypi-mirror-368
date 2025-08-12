# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.parameters_fetched_by_reading_cassandra_config_file
import cohesity_management_sdk.models_v2.hive_additional_params
import cohesity_management_sdk.models_v2.hb_ase_additional_params
import cohesity_management_sdk.models_v2.hdfs_additional_params

class TestConnectionResponseParameters(object):

    """Implementation of the 'Test Connection response parameters.' model.

    Specifies the response from a test connection request.

    Attributes:
        environment (Environment8Enum): Specifies the environment type of the
            Protection Source.
        cassandra_connection_response_params
            (ParametersFetchedByReadingCassandraConfigFile): Specifies the
            parameters fetched by reading cassandra configuration on the seed
            node.
        hive_connection_response_params (HiveAdditionalParams): Additional
            params for Hive protection source.
        hbase_connection_response_params (HBAseAdditionalParams): Additional
            params for HBase protection source.
        hdfs_connection_response_params (HdfsAdditionalParams): Additional
            params for Hdfs protection source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "environment":'environment',
        "cassandra_connection_response_params":'cassandraConnectionResponseParams',
        "hive_connection_response_params":'hiveConnectionResponseParams',
        "hbase_connection_response_params":'hbaseConnectionResponseParams',
        "hdfs_connection_response_params":'hdfsConnectionResponseParams'
    }

    def __init__(self,
                 environment=None,
                 cassandra_connection_response_params=None,
                 hive_connection_response_params=None,
                 hbase_connection_response_params=None,
                 hdfs_connection_response_params=None):
        """Constructor for the TestConnectionResponseParameters class"""

        # Initialize members of the class
        self.environment = environment
        self.cassandra_connection_response_params = cassandra_connection_response_params
        self.hive_connection_response_params = hive_connection_response_params
        self.hbase_connection_response_params = hbase_connection_response_params
        self.hdfs_connection_response_params = hdfs_connection_response_params


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
        cassandra_connection_response_params = cohesity_management_sdk.models_v2.parameters_fetched_by_reading_cassandra_config_file.ParametersFetchedByReadingCassandraConfigFile.from_dictionary(dictionary.get('cassandraConnectionResponseParams')) if dictionary.get('cassandraConnectionResponseParams') else None
        hive_connection_response_params = cohesity_management_sdk.models_v2.hive_additional_params.HiveAdditionalParams.from_dictionary(dictionary.get('hiveConnectionResponseParams')) if dictionary.get('hiveConnectionResponseParams') else None
        hbase_connection_response_params = cohesity_management_sdk.models_v2.hb_ase_additional_params.HBAseAdditionalParams.from_dictionary(dictionary.get('hbaseConnectionResponseParams')) if dictionary.get('hbaseConnectionResponseParams') else None
        hdfs_connection_response_params = cohesity_management_sdk.models_v2.hdfs_additional_params.HdfsAdditionalParams.from_dictionary(dictionary.get('hdfsConnectionResponseParams')) if dictionary.get('hdfsConnectionResponseParams') else None

        # Return an object of this model
        return cls(environment,
                   cassandra_connection_response_params,
                   hive_connection_response_params,
                   hbase_connection_response_params,
                   hdfs_connection_response_params)


