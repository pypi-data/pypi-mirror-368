# -*- coding: utf-8 -*-


class DeleteRigelConnectorRequest(object):

    """Implementation of the 'Delete Rigel Connector Request.' model.

    Specify the params to delete a Rigel connector.

    Attributes:
        tenant_id (string): Specifies the id of the tenant which the connector
            belongs to.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "tenant_id":'tenantId'
    }

    def __init__(self,
                 tenant_id=None):
        """Constructor for the DeleteRigelConnectorRequest class"""

        # Initialize members of the class
        self.tenant_id = tenant_id


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

        # Return an object of this model
        return cls(tenant_id)


