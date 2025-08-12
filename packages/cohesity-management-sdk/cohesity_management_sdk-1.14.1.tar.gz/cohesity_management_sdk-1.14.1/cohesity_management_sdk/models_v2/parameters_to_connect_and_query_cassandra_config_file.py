# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.ssh_password_credentials
import cohesity_management_sdk.models_v2.ssh_private_key_credentials

class ParametersToConnectAndQueryCassandraConfigFile(object):

    """Implementation of the 'Parameters to connect and query cassandra config file.' model.

    Specifies the parameters to connect to a Cassandra seed node and fetch
    information from its cassandra config file.

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

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "seed_node":'seedNode',
        "config_directory":'configDirectory',
        "is_dse_tiered_storage":'isDseTieredStorage',
        "is_dse_authenticator":'isDseAuthenticator',
        "dse_configuration_directory":'dseConfigurationDirectory',
        "ssh_password_credentials":'sshPasswordCredentials',
        "ssh_private_key_credentials":'sshPrivateKeyCredentials'
    }

    def __init__(self,
                 seed_node=None,
                 config_directory=None,
                 is_dse_tiered_storage=None,
                 is_dse_authenticator=None,
                 dse_configuration_directory=None,
                 ssh_password_credentials=None,
                 ssh_private_key_credentials=None):
        """Constructor for the ParametersToConnectAndQueryCassandraConfigFile class"""

        # Initialize members of the class
        self.seed_node = seed_node
        self.config_directory = config_directory
        self.dse_configuration_directory = dse_configuration_directory
        self.is_dse_tiered_storage = is_dse_tiered_storage
        self.is_dse_authenticator = is_dse_authenticator
        self.ssh_password_credentials = ssh_password_credentials
        self.ssh_private_key_credentials = ssh_private_key_credentials


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

        # Return an object of this model
        return cls(seed_node,
                   config_directory,
                   is_dse_tiered_storage,
                   is_dse_authenticator,
                   dse_configuration_directory,
                   ssh_password_credentials,
                   ssh_private_key_credentials)


