# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.ssh_password_credentials_3
import cohesity_management_sdk.models_v2.ssh_private_key_credentials_3

class RegisterHDFSSourceRequestParameters(object):

    """Implementation of the 'Register HDFS source request parameters.' model.

    Specifies parameters to register an HDFS source.

    Attributes:
        namenode_address (string): The HDFS Namenode IP or hostname.
        webhdfs_port (int): The HDFS WebHDFS port.
        auth_type (AuthTypeEnum): Authentication type.
        host (string): IP or hostname of any host from which the HDFS
            configuration files core-site.xml and hdfs-site.xml can be read.
        configuration_directory (string): The directory containing the
            core-site.xml and hdfs-site.xml configuration files.
        ssh_password_credentials (SshPasswordCredentials3): SSH username +
            password required for reading configuration file. Either
            'sshPasswordCredentials' or 'sshPrivateKeyCredentials' are
            required.
        ssh_private_key_credentials (SshPrivateKeyCredentials3): SSH  userID +
            privateKey required for reading configuration file.
        kerberos_principal (string): The kerberos principal to be used to
            connect to this HDFS source.
        hadoop_distribution (HadoopDistributionEnum): The hadoop distribution
            for this cluster. This can be either 'CDH' or 'HDP'
        hadoop_version (string): The hadoop version for this cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "host":'host',
        "configuration_directory":'configurationDirectory',
        "hadoop_distribution":'hadoopDistribution',
        "hadoop_version":'hadoopVersion',
        "namenode_address":'namenodeAddress',
        "webhdfs_port":'webhdfsPort',
        "auth_type":'authType',
        "ssh_password_credentials":'sshPasswordCredentials',
        "ssh_private_key_credentials":'sshPrivateKeyCredentials',
        "kerberos_principal":'kerberosPrincipal'
    }

    def __init__(self,
                 host=None,
                 configuration_directory=None,
                 hadoop_distribution=None,
                 hadoop_version=None,
                 namenode_address=None,
                 webhdfs_port=None,
                 auth_type=None,
                 ssh_password_credentials=None,
                 ssh_private_key_credentials=None,
                 kerberos_principal=None):
        """Constructor for the RegisterHDFSSourceRequestParameters class"""

        # Initialize members of the class
        self.namenode_address = namenode_address
        self.webhdfs_port = webhdfs_port
        self.auth_type = auth_type
        self.host = host
        self.configuration_directory = configuration_directory
        self.ssh_password_credentials = ssh_password_credentials
        self.ssh_private_key_credentials = ssh_private_key_credentials
        self.kerberos_principal = kerberos_principal
        self.hadoop_distribution = hadoop_distribution
        self.hadoop_version = hadoop_version


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
        hadoop_distribution = dictionary.get('hadoopDistribution')
        hadoop_version = dictionary.get('hadoopVersion')
        namenode_address = dictionary.get('namenodeAddress')
        webhdfs_port = dictionary.get('webhdfsPort')
        auth_type = dictionary.get('authType')
        ssh_password_credentials = cohesity_management_sdk.models_v2.ssh_password_credentials_3.SshPasswordCredentials3.from_dictionary(dictionary.get('sshPasswordCredentials')) if dictionary.get('sshPasswordCredentials') else None
        ssh_private_key_credentials = cohesity_management_sdk.models_v2.ssh_private_key_credentials_3.SshPrivateKeyCredentials3.from_dictionary(dictionary.get('sshPrivateKeyCredentials')) if dictionary.get('sshPrivateKeyCredentials') else None
        kerberos_principal = dictionary.get('kerberosPrincipal')

        # Return an object of this model
        return cls(host,
                   configuration_directory,
                   hadoop_distribution,
                   hadoop_version,
                   namenode_address,
                   webhdfs_port,
                   auth_type,
                   ssh_password_credentials,
                   ssh_private_key_credentials,
                   kerberos_principal)


