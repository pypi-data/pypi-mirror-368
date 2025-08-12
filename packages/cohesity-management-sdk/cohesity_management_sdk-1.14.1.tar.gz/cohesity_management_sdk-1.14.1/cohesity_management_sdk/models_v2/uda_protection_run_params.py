# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.uda_externally_triggered_run_params

class UdaProtectionRunParams(object):

    """Implementation of the 'UdaProtectionRunParams' model.

    Specifies the parameters for Universal Data Adapter protection run.

    Attributes:
        externally_triggered_run_params (UdaExternallyTriggeredRunParams): Specifies the parameters for an externally triggered run.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "externally_triggered_run_params":'externallyTriggeredRunParams'
    }

    def __init__(self,
                 externally_triggered_run_params=None):
        """Constructor for the UdaProtectionRunParams class"""

        # Initialize members of the class
        self.externally_triggered_run_params = externally_triggered_run_params

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
        externally_triggered_run_params = cohesity_management_sdk.models_v2.uda_externally_triggered_run_params.UdaExternallyTriggeredRunParams.from_dictionary(
            dictionary.get('externallyTriggeredRunParams')) if dictionary.get('externallyTriggeredRunParams') else None

        # Return an object of this model
        return cls(externally_triggered_run_params)