# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.ssh_password_credentials_7
import cohesity_management_sdk.models_v2.ssh_private_key_credentials_3

class RegisterHiveSourceRequestParameters(object):

    """Implementation of the 'Register Hive source request parameters.' model.

    Specifies parameters to register Hive source.

    Attributes:
        metastore_address (string): The MetastoreAddress for this Hive.
        metastore_port (int): The MetastorePort for this Hive.
        auth_type (AuthTypeEnum): Authentication type.
        host (string): IP or hostname of any host from which the Hive
            configuration file hive-site.xml can be read.
        configuration_directory (string): The directory containing the
            hive-site.xml.
        ssh_password_credentials (SshPasswordCredentials7): SSH username +
            password required for reading configuration file.Either
            'sshPasswordCredentials' or 'sshPrivateKeyCredentials' are
            required.
        ssh_private_key_credentials (SshPrivateKeyCredentials3): SSH  userID +
            privateKey required for reading configuration file.
        hdfs_source_registration_id (long|int): Protection Source registration
            id of the HDFS on which this Hive is running.
        kerberos_principal (string): The kerberos principal to be used to
            connect to this Hive source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "host":'host',
        "configuration_directory":'configurationDirectory',
        "hdfs_source_registration_id":'hdfsSourceRegistrationID',
        "metastore_address":'metastoreAddress',
        "metastore_port":'metastorePort',
        "auth_type":'authType',
        "ssh_password_credentials":'sshPasswordCredentials',
        "ssh_private_key_credentials":'sshPrivateKeyCredentials',
        "kerberos_principal":'kerberosPrincipal'
    }

    def __init__(self,
                 host=None,
                 configuration_directory=None,
                 hdfs_source_registration_id=None,
                 metastore_address=None,
                 metastore_port=None,
                 auth_type=None,
                 ssh_password_credentials=None,
                 ssh_private_key_credentials=None,
                 kerberos_principal=None):
        """Constructor for the RegisterHiveSourceRequestParameters class"""

        # Initialize members of the class
        self.metastore_address = metastore_address
        self.metastore_port = metastore_port
        self.auth_type = auth_type
        self.host = host
        self.configuration_directory = configuration_directory
        self.ssh_password_credentials = ssh_password_credentials
        self.ssh_private_key_credentials = ssh_private_key_credentials
        self.hdfs_source_registration_id = hdfs_source_registration_id
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
        hdfs_source_registration_id = dictionary.get('hdfsSourceRegistrationID')
        metastore_address = dictionary.get('metastoreAddress')
        metastore_port = dictionary.get('metastorePort')
        auth_type = dictionary.get('authType')
        ssh_password_credentials = cohesity_management_sdk.models_v2.ssh_password_credentials_7.SshPasswordCredentials7.from_dictionary(dictionary.get('sshPasswordCredentials')) if dictionary.get('sshPasswordCredentials') else None
        ssh_private_key_credentials = cohesity_management_sdk.models_v2.ssh_private_key_credentials_3.SshPrivateKeyCredentials3.from_dictionary(dictionary.get('sshPrivateKeyCredentials')) if dictionary.get('sshPrivateKeyCredentials') else None
        kerberos_principal = dictionary.get('kerberosPrincipal')

        # Return an object of this model
        return cls(host,
                   configuration_directory,
                   hdfs_source_registration_id,
                   metastore_address,
                   metastore_port,
                   auth_type,
                   ssh_password_credentials,
                   ssh_private_key_credentials,
                   kerberos_principal)


