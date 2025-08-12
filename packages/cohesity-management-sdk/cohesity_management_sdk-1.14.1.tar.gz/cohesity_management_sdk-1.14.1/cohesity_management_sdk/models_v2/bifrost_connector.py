# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.connection_info

class BifrostConnector(object):

    """Implementation of the 'Bifrost Connector.' model.

    Specify a Bifrost connector.

    Attributes:
        id (long|int): Specifies the id of the connector.
        name (string): Specifies the name of the connector.
        connection_id (long|int): Specifies the Id of the connection which
            this connector belongs to.
        connection_status (ConnectionInfo): Specifies the connection info of a
            connector.
        cohesity_side_ip (string): Specifies the cohesity side ip of the
            connector
        tenant_source_side_ip (string): Specifies the tenant source side ip of
            the connector
        hyx_version (string): Specifies the connector's software Version

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "connection_id":'connectionId',
        "connection_status":'connectionStatus',
        "cohesity_side_ip":'cohesitySideIp',
        "tenant_source_side_ip":'tenantSourceSideIp',
        "hyx_version":'hyxVersion'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 connection_id=None,
                 connection_status=None,
                 cohesity_side_ip=None,
                 tenant_source_side_ip=None,
                 hyx_version=None):
        """Constructor for the BifrostConnector class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.connection_id = connection_id
        self.connection_status = connection_status
        self.cohesity_side_ip = cohesity_side_ip
        self.tenant_source_side_ip = tenant_source_side_ip
        self.hyx_version = hyx_version


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
        connection_id = dictionary.get('connectionId')
        connection_status = cohesity_management_sdk.models_v2.connection_info.ConnectionInfo.from_dictionary(dictionary.get('connectionStatus')) if dictionary.get('connectionStatus') else None
        cohesity_side_ip = dictionary.get('cohesitySideIp')
        tenant_source_side_ip = dictionary.get('tenantSourceSideIp')
        hyx_version = dictionary.get('hyxVersion')

        # Return an object of this model
        return cls(id,
                   name,
                   connection_id,
                   connection_status,
                   cohesity_side_ip,
                   tenant_source_side_ip,
                   hyx_version)


