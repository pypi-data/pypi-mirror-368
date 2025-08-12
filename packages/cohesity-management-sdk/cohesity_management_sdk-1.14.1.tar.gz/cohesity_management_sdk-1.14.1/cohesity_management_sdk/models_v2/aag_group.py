# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.app_resource
import cohesity_management_sdk.models_v2.sql_server
import cohesity_management_sdk.models_v2.fci_cluster

class AAGGroup(object):

    """Implementation of the 'AAGGroup' model.

    Specifies the details of a AAG Group.

    Attributes:
        id (string): Specifies the unique identifier of the AGGGroup.
        name (string): Specifies the name of the AAG Group.
        resource_info (AppResource): Specifies the details about App
            Resource.
        servers (list of SQLServer): Specifies the list of SQL servers which
            belongs to the given AAG Group.
        fci_clusters (list of FCICluster): Specifies the list of FCI clusters
            which belongs to the given AAG Group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "resource_info":'resourceInfo',
        "servers":'servers',
        "fci_clusters":'fciClusters'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 resource_info=None,
                 servers=None,
                 fci_clusters=None):
        """Constructor for the AAGGroup class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.resource_info = resource_info
        self.servers = servers
        self.fci_clusters = fci_clusters


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
        id = dictionary.get('id')
        name = dictionary.get('name')
        resource_info = cohesity_management_sdk.models_v2.app_resource.AppResource.from_dictionary(dictionary.get('resourceInfo')) if dictionary.get('resourceInfo') else None
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

        # Return an object of this model
        return cls(id,
                   name,
                   resource_info,
                   servers,
                   fci_clusters)


