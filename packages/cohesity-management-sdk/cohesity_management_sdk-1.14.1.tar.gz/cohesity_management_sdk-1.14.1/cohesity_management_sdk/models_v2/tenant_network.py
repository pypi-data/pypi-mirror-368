# -*- coding: utf-8 -*-

class TenantNetwork(object):

    """Implementation of the 'TenantNetwork' model.

    Networking information about a Tenant on a Cluster.

    Attributes:
        cluster_hostname (string): The hostname for Cohesity cluster as seen by tenants and as
          is routable from the tenant''s network. Tenant''s VLAN''s hostname, if available can
          be used instead but it is mandatory to provide this value if there''s no VLAN
          hostname to use. Also, when set, this field would take precedence over VLAN hostname.
        cluster_ips (list of string): Set of IPs as seen from the tenant''s network for the Cohesity
          cluster.Only one from ''clusterHostname'' and ''clusterIps'' is needed.
        connector_enabled (bool): Whether connector (hybrid extender) is enabled.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cluster_hostname":'clusterHostname',
        "cluster_ips":'clusterIps',
        "connector_enabled":'connectorEnabled'
    }

    def __init__(self,
                 cluster_hostname=None,
                 cluster_ips=None,
                 connector_enabled=None,):
        """Constructor for the TenantNetwork class"""

        # Initialize members of the class
        self.cluster_hostname = cluster_hostname
        self.cluster_ips = cluster_ips
        self.connector_enabled = connector_enabled


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
        cluster_hostname = dictionary.get('clusterHostname')
        cluster_ips = dictionary.get('clusterIps')
        connector_enabled = dictionary.get('connectorEnabled')

        # Return an object of this model
        return cls(cluster_hostname,
                   cluster_ips,
                   connector_enabled)