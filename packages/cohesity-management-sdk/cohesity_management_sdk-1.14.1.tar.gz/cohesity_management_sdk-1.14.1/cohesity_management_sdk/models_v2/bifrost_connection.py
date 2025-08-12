# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.connection_subnet
import cohesity_management_sdk.models_v2.network_connection

class BifrostConnection(object):

    """Implementation of the 'Bifrost connection.' model.

    Specify a connection of Bifrost.

    Attributes:
        id (long|int): Specifies the id of the connection.
        name (string): Specifies the name of the connection.
        subnet (ConnectionSubnet): Specify the subnet used in connection.
        certificate_version (long|int): Specifies the version of the
            connection's certificate. The version is used to revoke/renew
            connection's certificates.
        network_connection_info (NetworkConnection): Specify the network
            connection information.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "subnet":'subnet',
        "certificate_version":'certificateVersion',
        "network_connection_info":'networkConnectionInfo'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 subnet=None,
                 certificate_version=None,
                 network_connection_info=None):
        """Constructor for the BifrostConnection class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.subnet = subnet
        self.certificate_version = certificate_version
        self.network_connection_info = network_connection_info


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
        subnet = cohesity_management_sdk.models_v2.connection_subnet.ConnectionSubnet.from_dictionary(dictionary.get('subnet')) if dictionary.get('subnet') else None
        certificate_version = dictionary.get('certificateVersion')
        network_connection_info = cohesity_management_sdk.models_v2.network_connection.NetworkConnection.from_dictionary(dictionary.get('networkConnectionInfo')) if dictionary.get('networkConnectionInfo') else None

        # Return an object of this model
        return cls(id,
                   name,
                   subnet,
                   certificate_version,
                   network_connection_info)


