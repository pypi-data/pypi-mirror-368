# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.resource_endpoint

class SQLServerInstance(object):

    """Implementation of the 'SQLServerInstance' model.

    Specifies the details of a SQL server.

    Attributes:
        id (string): Specifies the unique id of the SQL server instance.
        name (string): Specifies the name of the SQL server instance.
        is_online (string): Specifies the wehther the SQL server instance is
            online or not.
        endpoints (list of ResourceEndpoint): Specifies the information about
            endpoint associated with this SQL server instance.
        is_partof_fci (bool): Specifies whether this SQL server instance is a
            part of Failover cluster or not.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "is_online":'isOnline',
        "endpoints":'endpoints',
        "is_partof_fci":'isPartofFCI'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 is_online=None,
                 endpoints=None,
                 is_partof_fci=None):
        """Constructor for the SQLServerInstance class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.is_online = is_online
        self.endpoints = endpoints
        self.is_partof_fci = is_partof_fci


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
        is_online = dictionary.get('isOnline')
        endpoints = None
        if dictionary.get("endpoints") is not None:
            endpoints = list()
            for structure in dictionary.get('endpoints'):
                endpoints.append(cohesity_management_sdk.models_v2.resource_endpoint.ResourceEndpoint.from_dictionary(structure))
        is_partof_fci = dictionary.get('isPartofFCI')

        # Return an object of this model
        return cls(id,
                   name,
                   is_online,
                   endpoints,
                   is_partof_fci)


