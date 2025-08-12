# -*- coding: utf-8 -*-


class CreateRigelConnectionRequest(object):

    """Implementation of the 'Create Rigel Connection Request.' model.

    Specify the params to create a connection of Rigel.

    Attributes:
        tenant_id (string): Specifies the id of the tenant which the
            connection belongs to.
        name (string): Specifies the name of the connection.
        connection_id (long|int): Specifies the id of the connection.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "tenant_id":'tenantId',
        "name":'name',
        "connection_id":'connectionId'
    }

    def __init__(self,
                 tenant_id=None,
                 name=None,
                 connection_id=None):
        """Constructor for the CreateRigelConnectionRequest class"""

        # Initialize members of the class
        self.tenant_id = tenant_id
        self.name = name
        self.connection_id = connection_id


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
        tenant_id = dictionary.get('tenantId')
        name = dictionary.get('name')
        connection_id = dictionary.get('connectionId')

        # Return an object of this model
        return cls(tenant_id,
                   name,
                   connection_id)


