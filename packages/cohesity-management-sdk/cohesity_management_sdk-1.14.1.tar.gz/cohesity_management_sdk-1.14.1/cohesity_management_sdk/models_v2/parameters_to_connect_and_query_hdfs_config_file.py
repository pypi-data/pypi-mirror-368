# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.ssh_password_credentials_2
import cohesity_management_sdk.models_v2.ssh_private_key_credentials

class ParametersToConnectAndQueryHdfsConfigFile(object):

    """Implementation of the 'Parameters to connect and query hdfs config file.' model.

    Specifies the parameters to connect to a seed node and fetch information
    from its config file.

    Attributes:
        host (string): IP or hostname of any host from which the 
            configuration file can be read.
        configuration_directory (string): The directory containing the
            application specific config file. .
        ssh_password_credentials (SshPasswordCredentials2): SSH username +
            password required for reading configuration file and for scp
            backup.Either 'sshPasswordCredential' or 'sshPrivateKeyCredential'
            are required.
        ssh_private_key_credentials (SshPrivateKeyCredentials): SSH  userID +
            privateKey required for reading configuration file and for scp
            backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "host":'host',
        "configuration_directory":'configurationDirectory',
        "ssh_password_credentials":'sshPasswordCredentials',
        "ssh_private_key_credentials":'sshPrivateKeyCredentials'
    }

    def __init__(self,
                 host=None,
                 configuration_directory=None,
                 ssh_password_credentials=None,
                 ssh_private_key_credentials=None):
        """Constructor for the ParametersToConnectAndQueryHdfsConfigFile class"""

        # Initialize members of the class
        self.host = host
        self.configuration_directory = configuration_directory
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
        host = dictionary.get('host')
        configuration_directory = dictionary.get('configurationDirectory')
        ssh_password_credentials = cohesity_management_sdk.models_v2.ssh_password_credentials_2.SshPasswordCredentials2.from_dictionary(dictionary.get('sshPasswordCredentials')) if dictionary.get('sshPasswordCredentials') else None
        ssh_private_key_credentials = cohesity_management_sdk.models_v2.ssh_private_key_credentials.SshPrivateKeyCredentials.from_dictionary(dictionary.get('sshPrivateKeyCredentials')) if dictionary.get('sshPrivateKeyCredentials') else None

        # Return an object of this model
        return cls(host,
                   configuration_directory,
                   ssh_password_credentials,
                   ssh_private_key_credentials)


