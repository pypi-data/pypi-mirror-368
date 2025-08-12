# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.error
import cohesity_management_sdk.models_v2.sql_server
import cohesity_management_sdk.models_v2.fci_cluster
import cohesity_management_sdk.models_v2.aag_group

class MssqlConnectionResponseParams(object):

    """Implementation of the 'MssqlConnectionResponseParams' model.

    Specifies the response parameters after connecting to a SQL node/cluster
    using given IP or hostname FQDN.

    Attributes:
        host_identifier (string): Specifies the unique identifier to locate
            the SQL node or cluster. The host identifier can be IP address or
            FQDN.
        error (Error): Specifies the error object with error code and a
            message.
        skip_connection_discovery (bool): Specifies whether to skip the
            discovery phase of all SQL servers, AAG groups etc during
            registration process.
        servers (list of SQLServer): Specifies the list of SQL servers. If SQL
            server is a part of avalibility group then it will be returned in
            aagServers field. This will include the list of all standalone SQL
            servers and servers belonging to any FCI enviournment.
        fci_clusters (list of FCICluster): Specifies the list of FCI (Failover
            Cluster Instaces) Clusters. This will contain the list of all
            failover pools under a windows cluster. FCI clusters which are
            part of AAG, will be returned seperatly under aagServers field.
        aag_groups (list of AAGGroup): Specifies the list of AAG (Always on
            Avalibility) groups.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "host_identifier":'hostIdentifier',
        "error":'error',
        "skip_connection_discovery":'skipConnectionDiscovery',
        "servers":'servers',
        "fci_clusters":'fciClusters',
        "aag_groups":'aagGroups'
    }

    def __init__(self,
                 host_identifier=None,
                 error=None,
                 skip_connection_discovery=None,
                 servers=None,
                 fci_clusters=None,
                 aag_groups=None):
        """Constructor for the MssqlConnectionResponseParams class"""

        # Initialize members of the class
        self.host_identifier = host_identifier
        self.error = error
        self.skip_connection_discovery = skip_connection_discovery
        self.servers = servers
        self.fci_clusters = fci_clusters
        self.aag_groups = aag_groups


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
        host_identifier = dictionary.get('hostIdentifier')
        error = cohesity_management_sdk.models_v2.error.Error.from_dictionary(dictionary.get('error')) if dictionary.get('error') else None
        skip_connection_discovery = dictionary.get('skipConnectionDiscovery')
        servers = None
        if dictionary.get("servers") is not None:
            servers = list()
            for structure in dictionary.get('servers'):
                servers.append(cohesity_management_sdk.models_v2.sql_server.SQLServer.from_dictionary(structure))
        fci_clusters = None
        if dictionary.get("fciClusters") is not None:
            fci_clusters = list()
            for structure in dictionary.get('fciClusters'):
                fci_clusters.append(cohesity_management_sdk.models_v2.fci_cluster.FCICluster.from_dictionary(structure))
        aag_groups = None
        if dictionary.get("aagGroups") is not None:
            aag_groups = list()
            for structure in dictionary.get('aagGroups'):
                aag_groups.append(cohesity_management_sdk.models_v2.aag_group.AAGGroup.from_dictionary(structure))

        # Return an object of this model
        return cls(host_identifier,
                   error,
                   skip_connection_discovery,
                   servers,
                   fci_clusters,
                   aag_groups)


