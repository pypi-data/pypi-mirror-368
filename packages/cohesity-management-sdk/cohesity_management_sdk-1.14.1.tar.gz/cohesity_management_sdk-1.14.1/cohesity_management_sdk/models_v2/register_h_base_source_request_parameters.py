# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.ssh_password_credentials_3
import cohesity_management_sdk.models_v2.ssh_private_key_credentials_3

class RegisterHBaseSourceRequestParameters(object):

    """Implementation of the 'Register HBase source request parameters.' model.

    Specifies parameters to register an HBase source.

    Attributes:
        zookeeper_quorum (list of string): The 'Zookeeper Quorum' for this
            HBase.
        data_root_directory (string): The 'Data root directory' for this
            HBase.
        auth_type (AuthTypeEnum): Authentication type.
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
        hdfs_source_registration_id (long|int): Protection Source registration
            id of the HDFS on which this HBase is running.
        kerberos_principal (string): The kerberos principal to be used to
            connect to this Hbase source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "host":'host',
        "configuration_directory":'configurationDirectory',
        "hdfs_source_registration_id":'hdfsSourceRegistrationID',
        "zookeeper_quorum":'zookeeperQuorum',
        "data_root_directory":'dataRootDirectory',
        "auth_type":'authType',
        "ssh_password_credentials":'sshPasswordCredentials',
        "ssh_private_key_credentials":'sshPrivateKeyCredentials',
        "kerberos_principal":'kerberosPrincipal'
    }

    def __init__(self,
                 host=None,
                 configuration_directory=None,
                 hdfs_source_registration_id=None,
                 zookeeper_quorum=None,
                 data_root_directory=None,
                 auth_type=None,
                 ssh_password_credentials=None,
                 ssh_private_key_credentials=None,
                 kerberos_principal=None):
        """Constructor for the RegisterHBaseSourceRequestParameters class"""

        # Initialize members of the class
        self.zookeeper_quorum = zookeeper_quorum
        self.data_root_directory = data_root_directory
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
        zookeeper_quorum = dictionary.get('zookeeperQuorum')
        data_root_directory = dictionary.get('dataRootDirectory')
        auth_type = dictionary.get('authType')
        ssh_password_credentials = cohesity_management_sdk.models_v2.ssh_password_credentials_3.SshPasswordCredentials3.from_dictionary(dictionary.get('sshPasswordCredentials')) if dictionary.get('sshPasswordCredentials') else None
        ssh_private_key_credentials = cohesity_management_sdk.models_v2.ssh_private_key_credentials_3.SshPrivateKeyCredentials3.from_dictionary(dictionary.get('sshPrivateKeyCredentials')) if dictionary.get('sshPrivateKeyCredentials') else None
        kerberos_principal = dictionary.get('kerberosPrincipal')

        # Return an object of this model
        return cls(host,
                   configuration_directory,
                   hdfs_source_registration_id,
                   zookeeper_quorum,
                   data_root_directory,
                   auth_type,
                   ssh_password_credentials,
                   ssh_private_key_credentials,
                   kerberos_principal)