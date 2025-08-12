# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recovery_target_config_1
import cohesity_management_sdk.models_v2.aurora_config

class AwsTargetParams3(object):

    """Implementation of the 'AwsTargetParams3' model.

    Specifies the params for recovering to an AWS target.

    Attributes:
        recovery_target_config (RecoveryTargetConfig1): Specifies the recovery
            target configuration if recovery has to be done to a different
            location which is different from original source or to original
            Source with different configuration. If not specified, then the
            recovery of the vms will be performed to original location with
            all configuration parameters retained.
        aurora_config (AuroraConfig): Specifies the Aurora params.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_target_config":'recoveryTargetConfig',
        "aurora_config":'auroraConfig'
    }

    def __init__(self,
                 recovery_target_config=None,
                 aurora_config=None):
        """Constructor for the AwsTargetParams3 class"""

        # Initialize members of the class
        self.recovery_target_config = recovery_target_config
        self.aurora_config = aurora_config


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
        recovery_target_config = cohesity_management_sdk.models_v2.recovery_target_config_1.RecoveryTargetConfig1.from_dictionary(dictionary.get('recoveryTargetConfig')) if dictionary.get('recoveryTargetConfig') else None
        aurora_config = cohesity_management_sdk.models_v2.aurora_config.AuroraConfig.from_dictionary(dictionary.get('auroraConfig')) if dictionary.get('auroraConfig') else None

        # Return an object of this model
        return cls(recovery_target_config,
                   aurora_config)


