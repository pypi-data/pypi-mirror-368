# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.parameters_to_connect_and_query_cassandra_config_file
import cohesity_management_sdk.models_v2.parameters_to_connect_and_query_hdfs_config_file

class TestConnectionRequestParameters(object):

    """Implementation of the 'Test connection request parameters.' model.

    Specifies the parameters to test connectivity with a source.

    Attributes:
        environment (Environment8Enum): Specifies the environment type of the
            Protection Source.
        cassandra_connection_params
            (ParametersToConnectAndQueryCassandraConfigFile): Specifies the
            parameters to connect to a Cassandra seed node and fetch
            information from its cassandra config file.
        hive_connection_params (ParametersToConnectAndQueryHdfsConfigFile):
            Specifies the parameters to connect to a seed node and fetch
            information from its config file.
        hbase_connection_params (ParametersToConnectAndQueryHdfsConfigFile):
            Specifies the parameters to connect to a seed node and fetch
            information from its config file.
        hdfs_connection_params (ParametersToConnectAndQueryHdfsConfigFile):
            Specifies the parameters to connect to a seed node and fetch
            information from its config file.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "environment":'environment',
        "cassandra_connection_params":'cassandraConnectionParams',
        "hive_connection_params":'hiveConnectionParams',
        "hbase_connection_params":'hbaseConnectionParams',
        "hdfs_connection_params":'hdfsConnectionParams'
    }

    def __init__(self,
                 environment=None,
                 cassandra_connection_params=None,
                 hive_connection_params=None,
                 hbase_connection_params=None,
                 hdfs_connection_params=None):
        """Constructor for the TestConnectionRequestParameters class"""

        # Initialize members of the class
        self.environment = environment
        self.cassandra_connection_params = cassandra_connection_params
        self.hive_connection_params = hive_connection_params
        self.hbase_connection_params = hbase_connection_params
        self.hdfs_connection_params = hdfs_connection_params


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
        cassandra_connection_params = cohesity_management_sdk.models_v2.parameters_to_connect_and_query_cassandra_config_file.ParametersToConnectAndQueryCassandraConfigFile.from_dictionary(dictionary.get('cassandraConnectionParams')) if dictionary.get('cassandraConnectionParams') else None
        hive_connection_params = cohesity_management_sdk.models_v2.parameters_to_connect_and_query_hdfs_config_file.ParametersToConnectAndQueryHdfsConfigFile.from_dictionary(dictionary.get('hiveConnectionParams')) if dictionary.get('hiveConnectionParams') else None
        hbase_connection_params = cohesity_management_sdk.models_v2.parameters_to_connect_and_query_hdfs_config_file.ParametersToConnectAndQueryHdfsConfigFile.from_dictionary(dictionary.get('hbaseConnectionParams')) if dictionary.get('hbaseConnectionParams') else None
        hdfs_connection_params = cohesity_management_sdk.models_v2.parameters_to_connect_and_query_hdfs_config_file.ParametersToConnectAndQueryHdfsConfigFile.from_dictionary(dictionary.get('hdfsConnectionParams')) if dictionary.get('hdfsConnectionParams') else None

        # Return an object of this model
        return cls(environment,
                   cassandra_connection_params,
                   hive_connection_params,
                   hbase_connection_params,
                   hdfs_connection_params)


