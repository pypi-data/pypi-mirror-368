# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.cluster_network_config_1

class ClusterNetworkConfig3(object):

    """Implementation of the 'Cluster Network Config.' model.

    Specifies all of the parameters needed for network configuration of the
    new Cluster.

    Attributes:
        dhcp_network_config (ClusterDhcpNetworkConfig): Specifies the parameters needed for DHCP
            based network configuration.
        domain_names (list of string): Specifies the list of Domain Names new cluster should be configured
          with.
        manual_network_config (ClusterManualNetworkConfig): Specifies the parameters needed for
            manual network configuration.
        secondary_dhcp_network_config (ClusterDhcpNetworkConfig): Specifies the parameters needed for DHCP based secondary network
          configuration.
        secondary_manual_network_config (ClusterManualNetworkConfig): Specifies the parameters needed for manual secondary network
          configuration.
        use_dhcp (bool): Specifies whether or not to use DHCP to configure the network
          of the Cluster.
        ntp_servers (list of string): Specifies the list of NTP Servers new
            cluster should be configured with.
        ip_preference (IpPreferenceEnum): Specifies IP preference of the
            cluster to be Ipv4/Ipv6. It is Ipv4 by default.
        vip_host_name (string): Specifies the FQDN hostname of the cluster.
        vips (string): Virtual IPs to add to the cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "dhcp_network_config":'dhcpNetworkConfig',
        "domain_names":'domainNames',
        "manual_network_config":'manualNetworkConfig',
        "secondary_dhcp_network_config":'secondaryDhcpNetworkConfig',
        "secondary_manual_network_config":'secondaryManualNetworkConfig',
        "use_dhcp":'useDhcp',
        "ntp_servers":'ntpServers',
        "ip_preference":'ipPreference',
        "vip_host_name":'vipHostName',
        "vips":'vips'
    }

    def __init__(self,
                 dhcp_network_config=None,
                 domain_names=None,
                 manual_network_config=None,
                 secondary_dhcp_network_config=None,
                 secondary_manual_network_config=None,
                 use_dhcp=None,
                 ntp_servers=None,
                 ip_preference=None,
                 vip_host_name=None,
                 vips=None):
        """Constructor for the ClusterNetworkConfig3 class"""

        # Initialize members of the class
        self.dhcp_network_config = dhcp_network_config
        self.domain_names = domain_names
        self.manual_network_config = manual_network_config
        self.secondary_dhcp_network_config = secondary_dhcp_network_config
        self.secondary_manual_network_config = secondary_manual_network_config
        self.use_dhcp = use_dhcp
        self.ntp_servers = ntp_servers
        self.ip_preference = ip_preference
        self.vip_host_name = vip_host_name
        self.vips = vips


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
        dhcp_network_config = cohesity_management_sdk.models_v2.cluster_network_config_1.ClusterNetworkConfig1.from_dictionary(dictionary.get('dhcpNetworkConfig'))
        domain_names = dictionary.get('domainNames')
        manual_network_config = cohesity_management_sdk.models_v2.cluster_network_config_1.ClusterNetworkConfig1.from_dictionary(dictionary.get('manualNetworkConfig'))
        secondary_dhcp_network_config = cohesity_management_sdk.models_v2.cluster_network_config_1.ClusterNetworkConfig1.from_dictionary(dictionary.get('secondaryDhcpNetworkConfig')) if dictionary.get('secondaryDhcpNetworkConfig') else None
        secondary_manual_network_config = cohesity_management_sdk.models_v2.cluster_network_config_1.ClusterNetworkConfig1.from_dictionary(dictionary.get('secondaryManualNetworkConfig')) if dictionary.get('secondaryManualNetworkConfig') else None
        use_dhcp = dictionary.get('useDhcp')
        ip_preference = dictionary.get('ipPreference')
        vip_host_name = dictionary.get('vipHostName')
        ntp_servers = dictionary.get('ntpServers')
        vips = dictionary.get('vips')

        # Return an object of this model
        return cls(dhcp_network_config,
                   domain_names,
                   manual_network_config,
                   secondary_dhcp_network_config,
                   secondary_manual_network_config,
                   use_dhcp,
                   ntp_servers,
                   ip_preference,
                   vip_host_name,
                   vips)