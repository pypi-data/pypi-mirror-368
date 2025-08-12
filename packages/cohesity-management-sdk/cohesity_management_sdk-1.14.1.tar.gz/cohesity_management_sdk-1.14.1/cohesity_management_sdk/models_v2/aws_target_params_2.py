# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recovery_target_config_1
import cohesity_management_sdk.models_v2.rds_config

class AwsTargetParams2(object):

    """Implementation of the 'AwsTargetParams2' model.

    Specifies the params for recovering to an AWS target.

    Attributes:
        recovery_target_config (RecoveryTargetConfig1): Specifies the recovery
            target configuration if recovery has to be done to a different
            location which is different from original source or to original
            Source with different configuration. If not specified, then the
            recovery of the vms will be performed to original location with
            all configuration parameters retained.
        rds_config (RdsConfig): Specifies the RDS params.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_target_config":'recoveryTargetConfig',
        "rds_config":'rdsConfig'
    }

    def __init__(self,
                 recovery_target_config=None,
                 rds_config=None):
        """Constructor for the AwsTargetParams2 class"""

        # Initialize members of the class
        self.recovery_target_config = recovery_target_config
        self.rds_config = rds_config


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
        rds_config = cohesity_management_sdk.models_v2.rds_config.RdsConfig.from_dictionary(dictionary.get('rdsConfig')) if dictionary.get('rdsConfig') else None

        # Return an object of this model
        return cls(recovery_target_config,
                   rds_config)


