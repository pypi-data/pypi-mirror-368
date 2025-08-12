# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.rigel_connection

class RigelConnections(object):

    """Implementation of the 'Rigel connections.' model.

    Specify a list of connection of Rigel.

    Attributes:
        rigel_connections (list of RigelConnection): Specifies a list of
            connection of Rigel.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "rigel_connections":'RigelConnections'
    }

    def __init__(self,
                 rigel_connections=None):
        """Constructor for the RigelConnections class"""

        # Initialize members of the class
        self.rigel_connections = rigel_connections


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
        rigel_connections = None
        if dictionary.get("RigelConnections") is not None:
            rigel_connections = list()
            for structure in dictionary.get('RigelConnections'):
                rigel_connections.append(cohesity_management_sdk.models_v2.rigel_connection.RigelConnection.from_dictionary(structure))

        # Return an object of this model
        return cls(rigel_connections)


