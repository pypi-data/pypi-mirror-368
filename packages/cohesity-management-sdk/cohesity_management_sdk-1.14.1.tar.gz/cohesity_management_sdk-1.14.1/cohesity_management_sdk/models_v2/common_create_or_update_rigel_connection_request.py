# -*- coding: utf-8 -*-


class CommonCreateOrUpdateRigelConnectionRequest(object):

    """Implementation of the 'Common Create Or Update Rigel Connection Request.' model.

    Specify the common params to create or update a connection of Rigel.

    Attributes:
        tenant_id (string): Specifies the id of the tenant which the
            connection belongs to.
        name (string): Specifies the name of the connection.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "tenant_id":'tenantId',
        "name":'name'
    }

    def __init__(self,
                 tenant_id=None,
                 name=None):
        """Constructor for the CommonCreateOrUpdateRigelConnectionRequest class"""

        # Initialize members of the class
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
        tenant_id = dictionary.get('tenantId')
        name = dictionary.get('name')

        # Return an object of this model
        return cls(tenant_id,
                   name)


