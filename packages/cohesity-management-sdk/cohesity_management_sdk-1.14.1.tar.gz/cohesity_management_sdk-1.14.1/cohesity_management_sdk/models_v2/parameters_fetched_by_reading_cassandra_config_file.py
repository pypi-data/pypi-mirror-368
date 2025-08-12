# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.cassandra_specific_port_info
import cohesity_management_sdk.models_v2.cassandra_security_info

class ParametersFetchedByReadingCassandraConfigFile(object):

    """Implementation of the 'Parameters fetched by reading cassandra config file.' model.

    Specifies the parameters fetched by reading cassandra configuration on the
    seed node.

    Attributes:
        seeds (list of string): Seed nodes of this cluster.
        is_jmx_auth_enable (bool): Is JMX Authentication enabled in this
            cluster ?
        cassandra_port_info (CassandraSpecificPortInfo): Contains info about
            specific cassandra ports.
        cassandra_security_info (CassandraSecurityInfo): Cassandra security
            related info.
        data_center_names (list of string): Data centers for this cluster.
        commit_log_backup_location (string): Commit Logs backup location on
            cassandra nodes.
        endpoint_snitch (string): Endpoint snitch used for this cluster.
        cassandra_partitioner (string): Cassandra partitioner required in
            compaction.
        kerberos_sasl_protocol (string): Populated if cassandraAuthType is
            Kerberos.
        cassandra_version (string): Cassandra Version.
        dse_version (string): DSE Version

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "seeds":'seeds',
        "is_jmx_auth_enable":'isJmxAuthEnable',
        "cassandra_port_info":'cassandraPortInfo',
        "cassandra_security_info":'cassandraSecurityInfo',
        "data_center_names":'dataCenterNames',
        "commit_log_backup_location":'commitLogBackupLocation',
        "endpoint_snitch":'endpointSnitch',
        "cassandra_partitioner":'cassandraPartitioner',
        "kerberos_sasl_protocol":'kerberosSaslProtocol',
        "cassandra_version":'cassandraVersion',
        "dse_version":'dseVersion'
    }

    def __init__(self,
                 seeds=None,
                 is_jmx_auth_enable=None,
                 cassandra_port_info=None,
                 cassandra_security_info=None,
                 data_center_names=None,
                 commit_log_backup_location=None,
                 endpoint_snitch=None,
                 cassandra_partitioner=None,
                 kerberos_sasl_protocol=None,
                 cassandra_version=None,
                 dse_version=None):
        """Constructor for the ParametersFetchedByReadingCassandraConfigFile class"""

        # Initialize members of the class
        self.seeds = seeds
        self.is_jmx_auth_enable = is_jmx_auth_enable
        self.cassandra_port_info = cassandra_port_info
        self.cassandra_security_info = cassandra_security_info
        self.data_center_names = data_center_names
        self.commit_log_backup_location = commit_log_backup_location
        self.endpoint_snitch = endpoint_snitch
        self.cassandra_partitioner = cassandra_partitioner
        self.kerberos_sasl_protocol = kerberos_sasl_protocol
        self.cassandra_version = cassandra_version
        self.dse_version = dse_version


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
        seeds = dictionary.get('seeds')
        is_jmx_auth_enable = dictionary.get('isJmxAuthEnable')
        cassandra_port_info = cohesity_management_sdk.models_v2.cassandra_specific_port_info.CassandraSpecificPortInfo.from_dictionary(dictionary.get('cassandraPortInfo')) if dictionary.get('cassandraPortInfo') else None
        cassandra_security_info = cohesity_management_sdk.models_v2.cassandra_security_info.CassandraSecurityInfo.from_dictionary(dictionary.get('cassandraSecurityInfo')) if dictionary.get('cassandraSecurityInfo') else None
        data_center_names = dictionary.get('dataCenterNames')
        commit_log_backup_location = dictionary.get('commitLogBackupLocation')
        endpoint_snitch = dictionary.get('endpointSnitch')
        cassandra_partitioner = dictionary.get('cassandraPartitioner')
        kerberos_sasl_protocol = dictionary.get('kerberosSaslProtocol')
        cassandra_version = dictionary.get('cassandraVersion')
        dse_version = dictionary.get('dseVersion')

        # Return an object of this model
        return cls(seeds,
                   is_jmx_auth_enable,
                   cassandra_port_info,
                   cassandra_security_info,
                   data_center_names,
                   commit_log_backup_location,
                   endpoint_snitch,
                   cassandra_partitioner,
                   kerberos_sasl_protocol,
                   cassandra_version,
                   dse_version)


