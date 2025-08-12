# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.resource_endpoint

class AppResource(object):

    """Implementation of the 'AppResource' model.

    Specifies the details about App Resource.

    Attributes:
        id (string): Specifies the unique id of the app resource.
        mtype (TypeEnum): Specifies the type of the app resource.
        endpoints (list of ResourceEndpoint): Specifies the information about
            endpoint associated with this resorce.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "mtype":'type',
        "endpoints":'endpoints'
    }

    def __init__(self,
                 id=None,
                 mtype=None,
                 endpoints=None):
        """Constructor for the AppResource class"""

        # Initialize members of the class
        self.id = id
        self.mtype = mtype
        self.endpoints = endpoints


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
        mtype = dictionary.get('type')
        endpoints = None
        if dictionary.get("endpoints") is not None:
            endpoints = list()
            for structure in dictionary.get('endpoints'):
                endpoints.append(cohesity_management_sdk.models_v2.resource_endpoint.ResourceEndpoint.from_dictionary(structure))

        # Return an object of this model
        return cls(id,
                   mtype,
                   endpoints)


