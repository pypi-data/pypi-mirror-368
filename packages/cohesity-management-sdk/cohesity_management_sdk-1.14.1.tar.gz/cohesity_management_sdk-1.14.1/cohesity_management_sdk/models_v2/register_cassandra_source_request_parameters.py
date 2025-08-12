# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.ssh_password_credentials
import cohesity_management_sdk.models_v2.ssh_private_key_credentials
import cohesity_management_sdk.models_v2.jmx_credentials
import cohesity_management_sdk.models_v2.cassandra_credentials
import cohesity_management_sdk.models_v2.authentication_details_for_dse_solr

class RegisterCassandraSourceRequestParameters(object):

    """Implementation of the 'Register cassandra source request parameters.' model.

    Specifies parameters to register cassandra source.

    Attributes:
        seed_node (string): Any one seed node of the Cassandra cluster.
        config_directory (string): Directory path containing Cassandra
            configuration YAML file.
        dse_configuration_directory (string): Directory from where DSE
            specific configuration can be read. This should be set only when
            you are using the DSE distribution of Cassandra.
        is_dse_tiered_storage (bool): Set to true if this cluster has DSE
            tiered storage.
        is_dse_authenticator (bool): Set to true if this cluster has DSE
            Authenticator.
        ssh_password_credentials (SshPasswordCredentials): SSH username +
            password required for reading configuration file and for scp
            backup.Either 'sshPasswordCredentials' or
            'sshPrivateKeyCredentials' are required.
        ssh_private_key_credentials (SshPrivateKeyCredentials): SSH  userID +
            privateKey required for reading configuration file and for scp
            backup.
        jmx_credentials (JmxCredentials): JMX Credentials for this cluster.
            These should be the same for all the nodes
        cassandra_credentials (CassandraCredentials): Cassandra Credentials
            for this cluster.
        data_center_names (list of string): Data centers for this cluster.
        commit_log_backup_location (string): Commit Logs backup location on
            cassandra nodes.
        kerberos_principal (string): Principal for the kerberos connection.
            (This is required only if your Cassandra has Kerberos
            authentication. Please refer to the user guide.)
        dse_solr_info (AuthenticationDetailsForDSESolr): Contains details
            about DSE Solr.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "seed_node":'seedNode',
        "config_directory":'configDirectory',
        "is_dse_tiered_storage":'isDseTieredStorage',
        "is_dse_authenticator":'isDseAuthenticator',
        "dse_configuration_directory":'dseConfigurationDirectory',
        "ssh_password_credentials":'sshPasswordCredentials',
        "ssh_private_key_credentials":'sshPrivateKeyCredentials',
        "jmx_credentials":'jmxCredentials',
        "cassandra_credentials":'cassandraCredentials',
        "data_center_names":'dataCenterNames',
        "commit_log_backup_location":'commitLogBackupLocation',
        "kerberos_principal":'kerberosPrincipal',
        "dse_solr_info":'dseSolrInfo'
    }

    def __init__(self,
                 seed_node=None,
                 config_directory=None,
                 is_dse_tiered_storage=None,
                 is_dse_authenticator=None,
                 dse_configuration_directory=None,
                 ssh_password_credentials=None,
                 ssh_private_key_credentials=None,
                 jmx_credentials=None,
                 cassandra_credentials=None,
                 data_center_names=None,
                 commit_log_backup_location=None,
                 kerberos_principal=None,
                 dse_solr_info=None):
        """Constructor for the RegisterCassandraSourceRequestParameters class"""

        # Initialize members of the class
        self.seed_node = seed_node
        self.config_directory = config_directory
        self.dse_configuration_directory = dse_configuration_directory
        self.is_dse_tiered_storage = is_dse_tiered_storage
        self.is_dse_authenticator = is_dse_authenticator
        self.ssh_password_credentials = ssh_password_credentials
        self.ssh_private_key_credentials = ssh_private_key_credentials
        self.jmx_credentials = jmx_credentials
        self.cassandra_credentials = cassandra_credentials
        self.data_center_names = data_center_names
        self.commit_log_backup_location = commit_log_backup_location
        self.kerberos_principal = kerberos_principal
        self.dse_solr_info = dse_solr_info


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
        seed_node = dictionary.get('seedNode')
        config_directory = dictionary.get('configDirectory')
        is_dse_tiered_storage = dictionary.get('isDseTieredStorage')
        is_dse_authenticator = dictionary.get('isDseAuthenticator')
        dse_configuration_directory = dictionary.get('dseConfigurationDirectory')
        ssh_password_credentials = cohesity_management_sdk.models_v2.ssh_password_credentials.SshPasswordCredentials.from_dictionary(dictionary.get('sshPasswordCredentials')) if dictionary.get('sshPasswordCredentials') else None
        ssh_private_key_credentials = cohesity_management_sdk.models_v2.ssh_private_key_credentials.SshPrivateKeyCredentials.from_dictionary(dictionary.get('sshPrivateKeyCredentials')) if dictionary.get('sshPrivateKeyCredentials') else None
        jmx_credentials = cohesity_management_sdk.models_v2.jmx_credentials.JmxCredentials.from_dictionary(dictionary.get('jmxCredentials')) if dictionary.get('jmxCredentials') else None
        cassandra_credentials = cohesity_management_sdk.models_v2.cassandra_credentials.CassandraCredentials.from_dictionary(dictionary.get('cassandraCredentials')) if dictionary.get('cassandraCredentials') else None
        data_center_names = dictionary.get('dataCenterNames')
        commit_log_backup_location = dictionary.get('commitLogBackupLocation')
        kerberos_principal = dictionary.get('kerberosPrincipal')
        dse_solr_info = cohesity_management_sdk.models_v2.authentication_details_for_dse_solr.AuthenticationDetailsForDSESolr.from_dictionary(dictionary.get('dseSolrInfo')) if dictionary.get('dseSolrInfo') else None

        # Return an object of this model
        return cls(seed_node,
                   config_directory,
                   is_dse_tiered_storage,
                   is_dse_authenticator,
                   dse_configuration_directory,
                   ssh_password_credentials,
                   ssh_private_key_credentials,
                   jmx_credentials,
                   cassandra_credentials,
                   data_center_names,
                   commit_log_backup_location,
                   kerberos_principal,
                   dse_solr_info)


