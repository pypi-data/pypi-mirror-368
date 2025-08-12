# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.encryption_configuration_params

class CloudClusterParams(object):

    """Implementation of the 'Cloud Cluster Params.' model.

    Params for Cloud Edition Cluster Creation

    Attributes:
        cluster_partition_hostname (string): Hostname of the cluster partition.
        cluster_size (ClusterSizeEnum): Specifies the size of the cloud platforms.
        enable_cloud_rf1 (bool): Specifies whether or not to enable software encryption
        encryption_config (EncryptionConfigurationParams): Specifies the encryption configuration parameters
        ip_preference (long|int): Specifies IP preference
        metadata_fault_tolerance (long|int): Specifies the metadata fault tolerance.
        node_ips (list of string): TODO: type description here.
        trust_domain (string): Specifies Trust Domain used for Service Identity
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cluster_partition_hostname":'clusterPartitionHostname',
        "cluster_size":'clusterSize',
        "enable_cloud_rf1":'enableCloudRf1',
        "encryption_config":'encryptionConfig',
        "ip_preference":'ipPreference',
        "metadata_fault_tolerance":'metadataFaultTolerance',
        "node_ips":'nodeIps',
        "trust_domain":'trustDomain'
    }

    def __init__(self,
                 cluster_partition_hostname=None,
                 cluster_size=None,
                 enable_cloud_rf1=None,
                 encryption_config=None,
                 ip_preference=None,
                 metadata_fault_tolerance=None,
                 node_ips=None,
                 trust_domain=None
                 ):
        """Constructor for the CloudClusterParams class"""

        # Initialize members of the class
        self.cluster_partition_hostname = cluster_partition_hostname
        self.cluster_size = cluster_size
        self.enable_cloud_rf1 = enable_cloud_rf1
        self.encryption_config = encryption_config
        self.ip_preference = ip_preference
        self.metadata_fault_tolerance = metadata_fault_tolerance
        self.node_ips = node_ips
        self.trust_domain = trust_domain


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
        cluster_partition_hostname = dictionary.get('clusterPartitionHostname')
        cluster_size = dictionary.get('clusterSize')
        enable_cloud_rf1 = dictionary.get('enableCloudRf1')
        encryption_config = cohesity_management_sdk.models_v2.encryption_configuration_params.EncryptionConfigurationParams.from_dictionary(
            dictionary.get('encryptionConfig')) if dictionary.get('encryptionConfig') else None
        ip_preference = dictionary.get('ipPreference')
        metadata_fault_tolerance = dictionary.get('metadataFaultTolerance')
        node_ips = dictionary.get('nodeIps')
        trust_domain = dictionary.get('trustDomain')

        # Return an object of this model
        return cls(cluster_partition_hostname,
                   cluster_size,
                   enable_cloud_rf1,
                   encryption_config,
                   ip_preference,
                   metadata_fault_tolerance,
                   node_ips,
                   trust_domain)