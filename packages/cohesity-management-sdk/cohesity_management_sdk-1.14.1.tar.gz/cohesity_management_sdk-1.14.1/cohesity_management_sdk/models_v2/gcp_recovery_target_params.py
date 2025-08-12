# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.rename_recovered_vms_params
import cohesity_management_sdk.models_v2.recovery_target_config_7

class GCPRecoveryTargetParams(object):

    """Implementation of the 'GCP Recovery Target Params' model.

    Specifies the parameters for a GCP recovery target.

    Attributes:
        rename_recovered_vms_params (RenameRecoveredVmsParams): Specifies
            params to rename the VMs that are recovered. If not specified, the
            original names of the VMs are preserved.
        recovery_target_config (RecoveryTargetConfig7): Specifies the recovery
            target configuration if recovery has to be done to a different
            location which is different from original source or to original
            Source with different configuration. If not specified, then the
            recovery of the vms will be performed to original location with
            all configuration parameters retained.
        power_on_vms (bool): Specifies whether to power on vms after recovery.
            If not specified, or false, recovered vms will be in powered off
            state.
        continue_on_error (bool): Specifies whether to continue recovering
            other vms if one of vms failed to recover. Default value is
            false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "rename_recovered_vms_params":'renameRecoveredVmsParams',
        "recovery_target_config":'recoveryTargetConfig',
        "power_on_vms":'powerOnVms',
        "continue_on_error":'continueOnError'
    }

    def __init__(self,
                 rename_recovered_vms_params=None,
                 recovery_target_config=None,
                 power_on_vms=None,
                 continue_on_error=None):
        """Constructor for the GCPRecoveryTargetParams class"""

        # Initialize members of the class
        self.rename_recovered_vms_params = rename_recovered_vms_params
        self.recovery_target_config = recovery_target_config
        self.power_on_vms = power_on_vms
        self.continue_on_error = continue_on_error


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
        rename_recovered_vms_params = cohesity_management_sdk.models_v2.rename_recovered_vms_params.RenameRecoveredVmsParams.from_dictionary(dictionary.get('renameRecoveredVmsParams')) if dictionary.get('renameRecoveredVmsParams') else None
        recovery_target_config = cohesity_management_sdk.models_v2.recovery_target_config_7.RecoveryTargetConfig7.from_dictionary(dictionary.get('recoveryTargetConfig')) if dictionary.get('recoveryTargetConfig') else None
        power_on_vms = dictionary.get('powerOnVms')
        continue_on_error = dictionary.get('continueOnError')

        # Return an object of this model
        return cls(rename_recovered_vms_params,
                   recovery_target_config,
                   power_on_vms,
                   continue_on_error)


