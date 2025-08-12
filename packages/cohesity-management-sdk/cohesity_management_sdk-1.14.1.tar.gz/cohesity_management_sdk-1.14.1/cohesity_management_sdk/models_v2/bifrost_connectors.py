# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.bifrost_connector

class BifrostConnectors(object):

    """Implementation of the 'Bifrost Connectors.' model.

    Specify a list of Bifrost connectors.

    Attributes:
        bifrost_connectors (list of BifrostConnector): Specifies a list of
            Bifrost Connectors.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "bifrost_connectors":'BifrostConnectors'
    }

    def __init__(self,
                 bifrost_connectors=None):
        """Constructor for the BifrostConnectors class"""

        # Initialize members of the class
        self.bifrost_connectors = bifrost_connectors


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
        bifrost_connectors = None
        if dictionary.get("BifrostConnectors") is not None:
            bifrost_connectors = list()
            for structure in dictionary.get('BifrostConnectors'):
                bifrost_connectors.append(cohesity_management_sdk.models_v2.bifrost_connector.BifrostConnector.from_dictionary(structure))

        # Return an object of this model
        return cls(bifrost_connectors)


