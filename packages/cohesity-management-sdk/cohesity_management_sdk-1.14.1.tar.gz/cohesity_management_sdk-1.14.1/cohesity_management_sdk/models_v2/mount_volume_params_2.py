# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.hyperv_target_params_1

class MountVolumeParams2(object):

    """Implementation of the 'MountVolumeParams2' model.

    Specifies the parameters to mount HyperV Volumes.

    Attributes:
        target_environment (string): Specifies the environment of the recovery
            target. The corresponding params below must be filled out.
        hyperv_target_params (HypervTargetParams1): Specifies the params for
            recovering to a HyperV target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_environment":'targetEnvironment',
        "hyperv_target_params":'hypervTargetParams'
    }

    def __init__(self,
                 target_environment='kHyperV',
                 hyperv_target_params=None):
        """Constructor for the MountVolumeParams2 class"""

        # Initialize members of the class
        self.target_environment = target_environment
        self.hyperv_target_params = hyperv_target_params


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
        target_environment = dictionary.get("targetEnvironment") if dictionary.get("targetEnvironment") else 'kHyperV'
        hyperv_target_params = cohesity_management_sdk.models_v2.hyperv_target_params_1.HypervTargetParams1.from_dictionary(dictionary.get('hypervTargetParams')) if dictionary.get('hypervTargetParams') else None

        # Return an object of this model
        return cls(target_environment,
                   hyperv_target_params)


