# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.oracle_params_1

class ConstructMetaInfoParams(object):

    """Implementation of the 'ConstructMetaInfoParams' model.

    Params to construct meta info

    Attributes:
        environment (string): Specifies the environment type of the Protection
            group
        oracle_params (OracleParams1): Oracle Params to construct meta info
            for alternate restore or clone.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "environment":'environment',
        "oracle_params":'oracleParams'
    }

    def __init__(self,
                 environment='kOracle',
                 oracle_params=None):
        """Constructor for the ConstructMetaInfoParams class"""

        # Initialize members of the class
        self.environment = environment
        self.oracle_params = oracle_params


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
        environment = dictionary.get("environment") if dictionary.get("environment") else 'kOracle'
        oracle_params = cohesity_management_sdk.models_v2.oracle_params_1.OracleParams1.from_dictionary(dictionary.get('oracleParams')) if dictionary.get('oracleParams') else None

        # Return an object of this model
        return cls(environment,
                   oracle_params)


