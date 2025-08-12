# -*- coding: utf-8 -*-


class CreateOrUpdateBifrostConnectorRequest(object):

    """Implementation of the 'Create Or Update Bifrost connector Request.' model.

    Specify the params to create or update a Bifrost connector.

    Attributes:
        connection_id (long|int): Specifies the Id of the connection which
            this connector belongs to.
        tenant_id (string): Specifies the id of the tenant which the connector
            belongs to.
        name (string): Specifies the name of the connector.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "connection_id":'connectionId',
        "tenant_id":'tenantId',
        "name":'name'
    }

    def __init__(self,
                 connection_id=None,
                 tenant_id=None,
                 name=None):
        """Constructor for the CreateOrUpdateBifrostConnectorRequest class"""

        # Initialize members of the class
        self.connection_id = connection_id
        self.tenant_id = tenant_id
        self.name = name


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

        # Return an object of this model
        return cls(connection_id,
                   tenant_id,
                   name)


