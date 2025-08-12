# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.ssh_password_credentials_3
import cohesity_management_sdk.models_v2.ssh_private_key_credentials_3

class UpdateHBaseSourceRegistrationParameters(object):

    """Implementation of the 'Update HBase source registration parameters.' model.

    Specifies parameters to update registeration of an HBase source.

    Attributes:
        host (string): IP or hostname of any host from which the HBase
            configuration file hbase-site.xml can be read.
        configuration_directory (string): The directory containing the
            hbase-site.xml.
        ssh_password_credentials (SshPasswordCredentials3): SSH username +
            password required for reading configuration file. Either
            'sshPasswordCredentials' or 'sshPrivateKeyCredentials' are
            required.
        ssh_private_key_credentials (SshPrivateKeyCredentials3): SSH  userID +
            privateKey required for reading configuration file.
        kerberos_principal (string): The kerberos principal to be used to
            connect to this Hbase source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "host":'host',
        "configuration_directory":'configurationDirectory',
        "ssh_password_credentials":'sshPasswordCredentials',
        "ssh_private_key_credentials":'sshPrivateKeyCredentials',
        "kerberos_principal":'kerberosPrincipal'
    }

    def __init__(self,
                 host=None,
                 configuration_directory=None,
                 ssh_password_credentials=None,
                 ssh_private_key_credentials=None,
                 kerberos_principal=None):
        """Constructor for the UpdateHBaseSourceRegistrationParameters class"""

        # Initialize members of the class
        self.host = host
        self.configuration_directory = configuration_directory
        self.ssh_password_credentials = ssh_password_credentials
        self.ssh_private_key_credentials = ssh_private_key_credentials
        self.kerberos_principal = kerberos_principal


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
        ssh_password_credentials = cohesity_management_sdk.models_v2.ssh_password_credentials_3.SshPasswordCredentials3.from_dictionary(dictionary.get('sshPasswordCredentials')) if dictionary.get('sshPasswordCredentials') else None
        ssh_private_key_credentials = cohesity_management_sdk.models_v2.ssh_private_key_credentials_3.SshPrivateKeyCredentials3.from_dictionary(dictionary.get('sshPrivateKeyCredentials')) if dictionary.get('sshPrivateKeyCredentials') else None
        kerberos_principal = dictionary.get('kerberosPrincipal')

        # Return an object of this model
        return cls(host,
                   configuration_directory,
                   ssh_password_credentials,
                   ssh_private_key_credentials,
                   kerberos_principal)


