# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.error
import cohesity_management_sdk.models_v2.app_resource
import cohesity_management_sdk.models_v2.sql_server

class FCICluster(object):

    """Implementation of the 'FCICluster' model.

    Specifies the details of a Failover Cluster Instance.

    Attributes:
        id (string): Specifies the unique identifier of the FCI.
        name (string): Specifies the name of the FCI.
        error (Error): Specifies the error object with error code and a
            message.
        resource_info (AppResource): Specifies the details about App
            Resource.
        servers (list of SQLServer): Specifies the list of SQL servers which
            belongs to the given FCI.
        is_selected_by_default (bool): Indicates to the UI whether this FCI
            cluster should be selected by default

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "error":'error',
        "resource_info":'resourceInfo',
        "servers":'servers',
        "is_selected_by_default":'isSelectedByDefault'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 error=None,
                 resource_info=None,
                 servers=None,
                 is_selected_by_default=None):
        """Constructor for the FCICluster class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.error = error
        self.resource_info = resource_info
        self.servers = servers
        self.is_selected_by_default = is_selected_by_default


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
        error = cohesity_management_sdk.models_v2.error.Error.from_dictionary(dictionary.get('error')) if dictionary.get('error') else None
        resource_info = cohesity_management_sdk.models_v2.app_resource.AppResource.from_dictionary(dictionary.get('resourceInfo')) if dictionary.get('resourceInfo') else None
        servers = None
        if dictionary.get("servers") is not None:
            servers = list()
            for structure in dictionary.get('servers'):
                servers.append(cohesity_management_sdk.models_v2.sql_server.SQLServer.from_dictionary(structure))
        is_selected_by_default = dictionary.get('isSelectedByDefault')

        # Return an object of this model
        return cls(id,
                   name,
                   error,
                   resource_info,
                   servers,
                   is_selected_by_default)


