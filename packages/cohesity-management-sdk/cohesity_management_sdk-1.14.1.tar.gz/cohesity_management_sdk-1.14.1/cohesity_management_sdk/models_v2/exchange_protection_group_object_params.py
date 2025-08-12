# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.exchange_app_parameters

class ExchangeProtectionGroupObjectParams(object):

    """Implementation of the 'Exchange Protection Group Object Params.' model.

    Specifies the object identifier to for the exchange protection group.

    Attributes:
        id (long|int): Specifies the id of the registered Exchange
            DAG(Database Availability Group) source or Exchange physical
            source.
        name (string): Specifies the name of the registered Exchange
            DAG(Database Availability Group) source or Exchange physical
            source.
        app_params (list of ExchangeAppParameters): Specifies the specific
            parameters required for Exchange app configuration.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "app_params":'appParams'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 app_params=None):
        """Constructor for the ExchangeProtectionGroupObjectParams class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.app_params = app_params


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
        name = dictionary.get('name')
        app_params = None
        if dictionary.get("appParams") is not None:
            app_params = list()
            for structure in dictionary.get('appParams'):
                app_params.append(cohesity_management_sdk.models_v2.exchange_app_parameters.ExchangeAppParameters.from_dictionary(structure))

        # Return an object of this model
        return cls(id,
                   name,
                   app_params)


