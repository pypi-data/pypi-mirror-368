# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.exchange_target_params

class RecoverAppParams(object):

    """Implementation of the 'RecoverAppParams' model.

    Specifies the parameters to recover Exchange databases.

    Attributes:
        target_environment (string): Specifies the environment of the recovery
            target. The corresponding params below must be filled out.
        exchange_target_params (ExchangeTargetParams): Specifies the params
            for recovering to an Exchange host.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_environment":'targetEnvironment',
        "exchange_target_params":'exchangeTargetParams'
    }

    def __init__(self,
                 target_environment='kExchange',
                 exchange_target_params=None):
        """Constructor for the RecoverAppParams class"""

        # Initialize members of the class
        self.target_environment = target_environment
        self.exchange_target_params = exchange_target_params


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
        target_environment = dictionary.get("targetEnvironment") if dictionary.get("targetEnvironment") else 'kExchange'
        exchange_target_params = cohesity_management_sdk.models_v2.exchange_target_params.ExchangeTargetParams.from_dictionary(dictionary.get('exchangeTargetParams')) if dictionary.get('exchangeTargetParams') else None

        # Return an object of this model
        return cls(target_environment,
                   exchange_target_params)


