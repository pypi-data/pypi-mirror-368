# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.pure_target_params

class RecoverSanVolumeParams(object):

    """Implementation of the 'RecoverSanVolumeParams' model.

    Specifies the parameters to recover SAN Volume.

    Attributes:
        target_environment (string): Specifies the environment of the recovery
            target. The corresponding target params must be filled out.
        pure_target_params (PureTargetParams): Specifies the parameters of the
            Pure SAN volume to recover to.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_environment":'targetEnvironment',
        "pure_target_params":'pureTargetParams'
    }

    def __init__(self,
                 target_environment='kPure',
                 pure_target_params=None):
        """Constructor for the RecoverSanVolumeParams class"""

        # Initialize members of the class
        self.target_environment = target_environment
        self.pure_target_params = pure_target_params


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
        target_environment = dictionary.get("targetEnvironment") if dictionary.get("targetEnvironment") else 'kPure'
        pure_target_params = cohesity_management_sdk.models_v2.pure_target_params.PureTargetParams.from_dictionary(dictionary.get('pureTargetParams')) if dictionary.get('pureTargetParams') else None

        # Return an object of this model
        return cls(target_environment,
                   pure_target_params)


