
# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.node_specific_params
import cohesity_management_sdk.models_v2.node_config_params
import cohesity_management_sdk.models_v2.ipmi_configuration_params
import cohesity_management_sdk.models_v2.encryption_configuration_params
import cohesity_management_sdk.models_v2.node_group

class PhysicalClusterParams(object):

    """Implementation of the 'Physical Cluster Params.' model.

    Params for Physical Edition Cluster Creation

    Attributes:
        allow_api_based_fetch (bool): Specifies if API based GET should be enabled for cluster destroy
          params
        apps_subnet_ip (string): Specifies the IP for apps subnet
        apps_subnet_ip_v6 (string): Specifies the IPv6 for apps subnet
        apps_subnet_mask (string): Specifies the Mask for apps subnet
        apps_subnet_mask_v6 (string): Specifies the MaskV6 for apps subnet
        cluster_destroy_hmac_key (string): Specifies HMAC secret key that will be used to validate OTP used
          for destroy request
        cluster_subnet_groups (list of NodeGroup): List of cluster subnet groups this cluster should be configured
          with
        enable_cluster_destroy (bool): Specifies if cluster destroy op is enabled on this cluster
        encryption_config (EncryptionConfigurationParams): Specifies the encryption configuration parameters
        ip_preference (long|int): Specifies IP preference
        ipmi_config (IpmiConfigurationParams): Specifies the IPMI configuration parameters
        metadata_fault_tolerance (long|int): Specifies the metadata fault tolerance.
        node_configs (list of NodeConfigParams): Configuration of the nodes.
        nodes (list of NodeSpecificParams): TODO: type description here.
        trust_domain (string): Specifies Trust Domain used for Service Identity

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "allow_api_based_fetch":'allowApiBasedFetch',
        "apps_subnet_ip":'appsSubnetIp',
        "apps_subnet_ip_v6":'appsSubnetIpV6',
        "apps_subnet_mask":'appsSubnetMask',
        "apps_subnet_mask_v6":'appsSubnetMaskV6',
        "cluster_destroy_hmac_key":'clusterDestroyHmacKey',
        "cluster_subnet_groups":'clusterSubnetGroups',
        "enable_cluster_destroy":'enableClusterDestroy',
        "encryption_config":'encryptionConfig',
        "ip_preference":"ipPreference",
        "ipmi_config":'ipmiConfig',
        "metadata_fault_tolerance":'metadataFaultTolerance',
        "node_configs":'nodeConfigs',
        "nodes":'nodes',
        "trust_domain":'trustDomain'
    }

    def __init__(self,
                 allow_api_based_fetch=None,
                 apps_subnet_ip=None,
                 apps_subnet_ip_v6=None,
                 apps_subnet_mask=None,
                 apps_subnet_mask_v6=None,
                 cluster_destroy_hmac_key=None,
                 cluster_subnet_groups=None,
                 enable_cluster_destroy=None,
                 encryption_config=None,
                 ip_preference=None,
                 ipmi_config=None,
                 metadata_fault_tolerance = None,
                 node_configs=None,
                 nodes=None,
                 trust_domain=None):
        """Constructor for the PhysicalClusterParams class"""

        # Initialize members of the class
        self.allow_api_based_fetch = allow_api_based_fetch
        self.apps_subnet_ip = apps_subnet_ip
        self.apps_subnet_ip_v6 = apps_subnet_ip_v6
        self.apps_subnet_mask = apps_subnet_mask
        self.apps_subnet_mask_v6 = apps_subnet_mask_v6
        self.cluster_destroy_hmac_key = cluster_destroy_hmac_key
        self.cluster_subnet_groups = cluster_subnet_groups
        self.enable_cluster_destroy = enable_cluster_destroy
        self.encryption_config = encryption_config
        self.ip_preference = ip_preference
        self.ipmi_config = ipmi_config
        self.metadata_fault_tolerance = metadata_fault_tolerance
        self.node_configs = node_configs
        self.nodes = nodes
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
        allow_api_based_fetch = dictionary.get('allowApiBasedFetch')
        apps_subnet_ip = dictionary.get('appsSubnetIp')
        apps_subnet_ip_v6 = dictionary.get('appsSubnetIpV6')
        apps_subnet_mask = dictionary.get('appsSubnetMask')
        apps_subnet_mask_v6 = dictionary.get('appsSubnetMaskV6')
        cluster_destroy_hmac_key = dictionary.get('clusterDestroyHmacKey')
        cluster_subnet_groups = None
        if dictionary.get('clusterSubnetGroups') is not None:
            cluster_subnet_groups = list()
            for structure in dictionary.get('clusterSubnetGroups'):
                cluster_subnet_groups.append(cohesity_management_sdk.models_v2.node_group.NodeGroup.from_dictionary(structure))
        enable_cluster_destroy = dictionary.get('enableClusterDestroy')
        encryption_config = cohesity_management_sdk.models_v2.encryption_configuration_params.EncryptionConfigurationParams.from_dictionary(dictionary.get('encryptionConfig')) if dictionary.get('encryptionConfig') else None
        ip_preference = dictionary.get('ipPreference')
        ipmi_config = cohesity_management_sdk.models_v2.ipmi_configuration_params.IPMIConfigurationParams.from_dictionary(dictionary.get('ipmiConfig')) if dictionary.get('ipmiConfig') else None
        metadata_fault_tolerance = dictionary.get('metadataFaultTolerance')
        node_configs = None
        if dictionary.get('nodeConfigs') is not None:
            node_configs = list()
            for structure in dictionary.get('nodeConfigs'):
                node_configs.append(cohesity_management_sdk.models_v2.node_config_params.NodeConfigParams.from_dictionary(structure))
        nodes = None
        if dictionary.get("nodes") is not None:
            nodes = list()
            for structure in dictionary.get('nodes'):
                nodes.append(cohesity_management_sdk.models_v2.node_specific_params.NodeSpecificParams.from_dictionary(structure))
        trust_domain = dictionary.get('trustDomain')

        # Return an object of this model
        return cls(
            allow_api_based_fetch,
            apps_subnet_ip,
            apps_subnet_ip_v6,
            apps_subnet_mask,
            apps_subnet_mask_v6,
            cluster_destroy_hmac_key,
            cluster_subnet_groups,
            enable_cluster_destroy,
            encryption_config,
            ip_preference,
            ipmi_config,
            metadata_fault_tolerance,
            node_configs,
            nodes,
            trust_domain)