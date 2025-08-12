# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vmware_target_params_1
import cohesity_management_sdk.models_v2.restore_object_customization
import cohesity_management_sdk.models_v2.recover_protection_group_run_params

class RecoverVmwareVMParams(object):

    """Implementation of the 'Recover VMware VM params.' model.

    Specifies the parameters to recover VMware VM.

    Attributes:
        recover_protection_group_runs_params (list of RecoverProtectionGroupRunParams): Specifies the Protection Group Runs params to recover. All the
          VM's that are successfully backed up by specified Runs will be recovered.
          This can be specified along with individual snapshots of VMs. User has to
          make sure that specified Object snapshots and Protection Group Runs should
          not have any intersection. For example, user cannot specify multiple Runs
          which has same Object or an Object snapshot and a Run which has same Object's
          snapshot.
        restore_object_customizations (list of RestoreObjectCustomization): Specifies the customization
            for the VMs being restored.
        target_environment (string): Specifies the environment of the recovery
            target. The corresponding params below must be filled out.
        vmware_target_params (VmwareTargetParams1): Specifies the params for
            recovering to a VMware target.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recover_protection_group_runs_params":'recoverProtectionGroupRunsParams',
        "restore_object_customizations":'restoreObjectCustomizations',
        "target_environment":'targetEnvironment',
        "vmware_target_params":'vmwareTargetParams'
    }

    def __init__(self,
                 recover_protection_group_runs_params=None,
                 restore_object_customizations=None,
                 target_environment='kVMware',
                 vmware_target_params=None):
        """Constructor for the RecoverVmwareVMParams class"""

        # Initialize members of the class
        self.recover_protection_group_runs_params = recover_protection_group_runs_params
        self.restore_object_customizations = restore_object_customizations
        self.target_environment = target_environment
        self.vmware_target_params = vmware_target_params


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
        recover_protection_group_runs_params = None
        if dictionary.get("recoverProtectionGroupRunsParams") is not None:
            recover_protection_group_runs_params = list()
            for structure in dictionary.get('recoverProtectionGroupRunsParams'):
                recover_protection_group_runs_params.append(cohesity_management_sdk.models_v2.recover_protection_group_run_params.RecoverProtectionGroupRunParams.from_dictionary(structure))
        restore_object_customizations = None
        if dictionary.get("restoreObjectCustomizations") is not None:
            restore_object_customizations = list()
            for structure in dictionary.get('restoreObjectCustomizations'):
                restore_object_customizations.append(cohesity_management_sdk.models_v2.restore_object_customization.RestoreObjectCustomization.from_dictionary(structure))
        target_environment = dictionary.get("targetEnvironment") if dictionary.get("targetEnvironment") else 'kVMware'
        vmware_target_params = cohesity_management_sdk.models_v2.vmware_target_params_1.VmwareTargetParams1.from_dictionary(dictionary.get('vmwareTargetParams')) if dictionary.get('vmwareTargetParams') else None

        # Return an object of this model
        return cls(recover_protection_group_runs_params,
                   restore_object_customizations,
                   target_environment,
                   vmware_target_params)