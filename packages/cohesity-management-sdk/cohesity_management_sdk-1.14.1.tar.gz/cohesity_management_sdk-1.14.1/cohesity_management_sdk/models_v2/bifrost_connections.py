# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.bifrost_connection

class BifrostConnections(object):

    """Implementation of the 'Bifrost connections.' model.

    Specify a list of connection of Bifrost.

    Attributes:
        bifrost_connections (list of BifrostConnection): Specifies a list of
            connection of Bifrost.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "bifrost_connections":'BifrostConnections'
    }

    def __init__(self,
                 bifrost_connections=None):
        """Constructor for the BifrostConnections class"""

        # Initialize members of the class
        self.bifrost_connections = bifrost_connections


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
        bifrost_connections = None
        if dictionary.get("BifrostConnections") is not None:
            bifrost_connections = list()
            for structure in dictionary.get('BifrostConnections'):
                bifrost_connections.append(cohesity_management_sdk.models_v2.bifrost_connection.BifrostConnection.from_dictionary(structure))

        # Return an object of this model
        return cls(bifrost_connections)


