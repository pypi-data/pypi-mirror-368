# -*- coding: utf-8 -*-


class CommonCreateOrUpdateRigelConnectorRequest(object):

    """Implementation of the 'Common Create Or Update Rigel connector Request.' model.

    Specify the common params to create or update a Rigel connector.

    Attributes:
        connection_id (long|int): Specifies the Id of the connection which
            this connector belongs to.
        tenant_id (string): Specifies the id of the tenant which the connector
            belongs to.
        name (string): Specifies the name of the connector.
        certificate_version (long|int): Specifies the version of the
            connector's certificate. The version is used to revoke/renew
            connector's certificates.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "connection_id":'connectionId',
        "tenant_id":'tenantId',
        "name":'name',
        "certificate_version":'certificateVersion'
    }

    def __init__(self,
                 connection_id=None,
                 tenant_id=None,
                 name=None,
                 certificate_version=None):
        """Constructor for the CommonCreateOrUpdateRigelConnectorRequest class"""

        # Initialize members of the class
        self.connection_id = connection_id
        self.tenant_id = tenant_id
        self.name = name
        self.certificate_version = certificate_version


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
        connection_id = dictionary.get('connectionId')
        tenant_id = dictionary.get('tenantId')
        name = dictionary.get('name')
        certificate_version = dictionary.get('certificateVersion')

        # Return an object of this model
        return cls(connection_id,
                   tenant_id,
                   name,
                   certificate_version)


