# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_universal_data_adapter_params

class RecoverUniversalDataAdapterEnvironmentParams(object):

    """Implementation of the 'Recover Universal Data Adapter environment params.' model.

    Specifies the recovery options specific to Universal Data Adapter
    environment.

    Attributes:
        recovery_action (string): Specifies the type of recover action to be
            performed.
        recover_uda_params (RecoverUniversalDataAdapterParams): Specifies the
            parameters to recover Universal Data Adapter objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_action":'recoveryAction',
        "recover_uda_params":'recoverUdaParams'
    }

    def __init__(self,
                 recovery_action='RecoverObjects',
                 recover_uda_params=None):
        """Constructor for the RecoverUniversalDataAdapterEnvironmentParams class"""

        # Initialize members of the class
        self.recovery_action = recovery_action
        self.recover_uda_params = recover_uda_params


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
        recovery_action = dictionary.get("recoveryAction") if dictionary.get("recoveryAction") else 'RecoverObjects'
        recover_uda_params = cohesity_management_sdk.models_v2.recover_universal_data_adapter_params.RecoverUniversalDataAdapterParams.from_dictionary(dictionary.get('recoverUdaParams')) if dictionary.get('recoverUdaParams') else None

        # Return an object of this model
        return cls(recovery_action,
                   recover_uda_params)


