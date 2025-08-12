# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.



class AdditionalEwsExchangeConnectorParams(object):

    """Implementation of the 'AdditionalEwsExchangeConnectorParams' model.

    Message that encapsulates the additional connector params for the EWS
      Exchange environment.


    Attributes:
        auth_method (int): The authentication method to be used to login to the server.
          Specific to agent connector contexts.
        use_proxy (bool): Specifies whether to use the cluster config proxy settings.
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "auth_method": 'authMethod',
        "use_proxy": 'useProxy'
    }
    def __init__(self,
                 auth_method = None,
                 use_proxy = None
            ):

        """Constructor for the AdditionalEwsExchangeConnectorParams class"""

        # Initialize members of the class
        self.auth_method = auth_method
        self.use_proxy = use_proxy

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
        auth_method = dictionary.get('authMethod')
        use_proxy = dictionary.get('useProxy')

        # Return an object of this model
        return cls(
            auth_method,
            use_proxy
)