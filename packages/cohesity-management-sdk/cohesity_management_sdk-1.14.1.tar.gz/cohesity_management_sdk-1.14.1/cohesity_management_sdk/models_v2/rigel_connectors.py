# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.rigel_connector

class RigelConnectors(object):

    """Implementation of the 'Rigel Connectors.' model.

    Specify a list of Rigel connectors.

    Attributes:
        rigel_connectors (list of RigelConnector): Specifies a list of Rigel
            Connectors.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "rigel_connectors":'RigelConnectors'
    }

    def __init__(self,
                 rigel_connectors=None):
        """Constructor for the RigelConnectors class"""

        # Initialize members of the class
        self.rigel_connectors = rigel_connectors


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
        rigel_connectors = None
        if dictionary.get("RigelConnectors") is not None:
            rigel_connectors = list()
            for structure in dictionary.get('RigelConnectors'):
                rigel_connectors.append(cohesity_management_sdk.models_v2.rigel_connector.RigelConnector.from_dictionary(structure))

        # Return an object of this model
        return cls(rigel_connectors)


