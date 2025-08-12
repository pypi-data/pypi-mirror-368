# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_app_params_1

class RecoverExchangeEnvironmentParams(object):

    """Implementation of the 'Recover Exchange environment params.' model.

    Specifies the recovery options specific to Exchange environment.

    Attributes:
        recovery_action (string): Specifies the type of recover action to be
            performed.
        recover_app_params (RecoverAppParams1): Specifies the parameters to
            recover Exchange databases.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_action":'recoveryAction',
        "recover_app_params":'recoverAppParams'
    }

    def __init__(self,
                 recovery_action='RecoverApps',
                 recover_app_params=None):
        """Constructor for the RecoverExchangeEnvironmentParams class"""

        # Initialize members of the class
        self.recovery_action = recovery_action
        self.recover_app_params = recover_app_params


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
        recovery_action = dictionary.get("recoveryAction") if dictionary.get("recoveryAction") else 'RecoverApps'
        recover_app_params = cohesity_management_sdk.models_v2.recover_app_params_1.RecoverAppParams1.from_dictionary(dictionary.get('recoverAppParams')) if dictionary.get('recoverAppParams') else None

        # Return an object of this model
        return cls(recovery_action,
                   recover_app_params)


