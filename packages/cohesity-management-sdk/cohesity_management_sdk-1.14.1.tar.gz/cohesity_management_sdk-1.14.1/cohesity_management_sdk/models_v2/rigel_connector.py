# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.connection_info

class RigelConnector(object):

    """Implementation of the 'Rigel Connector.' model.

    Specify a Rigel connector.

    Attributes:
        id (long|int): Specifies the id of the connector.
        name (string): Specifies the name of the connector.
        connection_id (long|int): Specifies the Id of the connection which
            this connector belongs to.
        certificate_version (long|int): Specifies the version of the
            connector's certificate. The version is used to revoke/renew
            connector's certificates.
        connection_status (ConnectionInfo): Specifies the connection info of a
            connector.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "connection_id":'connectionId',
        "certificate_version":'certificateVersion',
        "connection_status":'connectionStatus'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 connection_id=None,
                 certificate_version=None,
                 connection_status=None):
        """Constructor for the RigelConnector class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.connection_id = connection_id
        self.certificate_version = certificate_version
        self.connection_status = connection_status


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
        certificate_version = dictionary.get('certificateVersion')
        connection_status = cohesity_management_sdk.models_v2.connection_info.ConnectionInfo.from_dictionary(dictionary.get('connectionStatus')) if dictionary.get('connectionStatus') else None

        # Return an object of this model
        return cls(id,
                   name,
                   connection_id,
                   certificate_version,
                   connection_status)


