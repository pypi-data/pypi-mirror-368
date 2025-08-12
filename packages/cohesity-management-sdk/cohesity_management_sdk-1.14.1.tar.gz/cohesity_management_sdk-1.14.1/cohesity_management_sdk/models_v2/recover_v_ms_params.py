# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_protection_group_run_params
import cohesity_management_sdk.models_v2.hyperv_target_params_5

class RecoverVMsParams(object):

    """Implementation of the 'Recover VMs params.' model.

    Specifies the parameters to recover VMs.

    Attributes:
        recover_protection_group_runs_params (list of
            RecoverProtectionGroupRunParams): Specifies the Protection Group
            Runs params to recover. All the VM's that are successfully backed
            up by specified Runs will be recovered. This can be specified
            along with individual snapshots of VMs. User has to make sure that
            specified Object snapshots and Protection Group Runs should not
            have any intersection. For example, user cannot specify multiple
            Runs which has same Object or an Object snapshot and a Run which
            has same Object's snapshot.
        target_environment (string): Specifies the environment of the recovery
            target. The corresponding params below must be filled out.
        hyperv_target_params (HypervTargetParams5): Specifies the params for
            recovering to a HyperV target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_environment":'targetEnvironment',
        "recover_protection_group_runs_params":'recoverProtectionGroupRunsParams',
        "hyperv_target_params":'hypervTargetParams'
    }

    def __init__(self,
                 target_environment='kHyperV',
                 recover_protection_group_runs_params=None,
                 hyperv_target_params=None):
        """Constructor for the RecoverVMsParams class"""

        # Initialize members of the class
        self.recover_protection_group_runs_params = recover_protection_group_runs_params
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
        recover_protection_group_runs_params = None
        if dictionary.get("recoverProtectionGroupRunsParams") is not None:
            recover_protection_group_runs_params = list()
            for structure in dictionary.get('recoverProtectionGroupRunsParams'):
                recover_protection_group_runs_params.append(cohesity_management_sdk.models_v2.recover_protection_group_run_params.RecoverProtectionGroupRunParams.from_dictionary(structure))
        hyperv_target_params = cohesity_management_sdk.models_v2.hyperv_target_params_5.HypervTargetParams5.from_dictionary(dictionary.get('hypervTargetParams')) if dictionary.get('hypervTargetParams') else None

        # Return an object of this model
        return cls(target_environment,
                   recover_protection_group_runs_params,
                   hyperv_target_params)


