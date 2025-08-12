# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.oracle_params_2

class ConstructMetaInfoResult(object):

    """Implementation of the 'ConstructMetaInfoResult' model.

    Result to store meta-info from an object snapshot and additional
    information.

    Attributes:
        environment (Environment14Enum): Specifies the environment type of the
            Protection group
        oracle_params (OracleParams2): Specifies 3 Maps required to fill pfile
            text box.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "environment":'environment',
        "oracle_params":'oracleParams'
    }

    def __init__(self,
                 environment=None,
                 oracle_params=None):
        """Constructor for the ConstructMetaInfoResult class"""

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
        environment = dictionary.get('environment')
        oracle_params = cohesity_management_sdk.models_v2.oracle_params_2.OracleParams2.from_dictionary(dictionary.get('oracleParams')) if dictionary.get('oracleParams') else None

        # Return an object of this model
        return cls(environment,
                   oracle_params)


