# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_or_clone_vm_s_rename_config_params
import cohesity_management_sdk.models_v2.recovery_target_config_5
import cohesity_management_sdk.models_v2.vlan_config_1


class VmwareTargetParams3(object):

    """Implementation of the 'VmwareTargetParams3' model.

    Specifies the params for recovering to a VMware target.

    Attributes:
        attempt_differential_restore (bool): Specifies whether to attempt differential restore.
        rename_recovered_v_apps_params (RecoverOrCloneVMsRenameConfigparams): Specifies params to rename the vApps that are recovered. If not
          specified, the original names of the vApps are preserved.
        continue_on_error (bool): Specifies whether to continue recovering other vms if one of
          vms failed to recover. Default value is false.
        disk_provision_type (DiskProvisionTYpeEnum): Specifies the Virtual Disk Provisioning Policies
            for Vmware VM
        enable_nbdssl_fallback (bool): If this field is set to true and SAN transport recovery fails,
          then recovery will fallback to use NBDSSL transport. This field only applies
          if 'leverageSanTransport' is set to true.
        leverage_san_transport (bool): Specifies whether to enable SAN transport for copy recovery or
          not
        power_on_vms (bool): Specifies whether to power on vms after recovery. If not specified,
          or false, recovered vms will be in powered off state.
        recovery_process_type (RecoveryProcessType1Enum): Specifies type of Recovery Process to be used. InstantRecovery/CopyRecovery
          etc... Default value is InstantRecovery.
        recovery_target_config (VmwareVmRecoveryTargetConfig): Specifies params to rename the VMs that are recovered. If not
          specified, the original names of the VMs are preserved.
        rename_recovered_vms_params (RecoverOrCloneVMsRenameConfigparams): Specifies params to rename the VMs that are recovered. If not
          specified, the original names of the VMs are preserved.
        vlan_config (VlanConfig1): Specifies VLAN Params associated with the
            recovered. If this is not specified, then the VLAN settings will
            be automatically selected from one of the below options: a. If
            VLANs are configured on Cohesity, then the VLAN host/VIP will be
            automatically based on the client's (e.g. ESXI host) IP address.
            b. If VLANs are not configured on Cohesity, then the partition
            hostname or VIPs will be used for Recovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "attempt_differential_restore":'attemptDifferentialRestore',
        "rename_recovered_v_apps_params":'renameRecoveredVAppsParams',
        "continue_on_error":'continueOnError',
        "disk_provision_type":'diskProvisionType',
        "enable_nbdssl_fallback":'enableNBDSSLFallback',
        "leverage_san_transport":'leverageSanTransport',
        "power_on_vms":'powerOnVms',
        "recovery_process_type":'recoveryProcessType',
        "recovery_target_config":'recoveryTargetConfig',
        "rename_recovered_vms_params":'renameRecoveredVmsParams',
        "vlan_config":'vlanConfig'
    }

    def __init__(self,
                 attempt_differential_restore=None,
                 rename_recovered_v_apps_params=None,
                 continue_on_error=None,
                 disk_provision_type=None,
                 enable_nbdssl_fallback=None,
                 leverage_san_transport=None,
                 power_on_vms=None,
                 recovery_process_type=None,
                 recovery_target_config=None,
                 rename_recovered_vms_params=None,
                 vlan_config=None
                 ):
        """Constructor for the VmwareTargetParams1 class"""

        # Initialize members of the class
        self.attempt_differential_restore = attempt_differential_restore
        self.rename_recovered_v_apps_params = rename_recovered_v_apps_params
        self.continue_on_error = continue_on_error
        self.disk_provision_type = disk_provision_type
        self.enable_nbdssl_fallback = enable_nbdssl_fallback
        self.leverage_san_transport = leverage_san_transport
        self.power_on_vms = power_on_vms
        self.recovery_process_type = recovery_process_type
        self.recovery_target_config = recovery_target_config
        self.rename_recovered_vms_params = rename_recovered_vms_params
        self.vlan_config = vlan_config



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
        attempt_differential_restore = dictionary.get('attemptDifferentialRestore')
        rename_recovered_v_apps_params = cohesity_management_sdk.models_v2.recover_or_clone_vm_s_rename_config_params.RecoverOrCloneVMsRenameConfigparams.from_dictionary(
            dictionary.get('renameRecoveredVAppsParams')) if dictionary.get('renameRecoveredVAppsParams') else None
        continue_on_error = dictionary.get('continueOnError')
        disk_provision_type = dictionary.get('diskProvisionType')
        enable_nbdssl_fallback = dictionary.get('enableNBDSSLFallback')
        leverage_san_transport = dictionary.get('leverageSanTransport')
        power_on_vms = dictionary.get('powerOnVms')
        recovery_process_type = dictionary.get('recoveryProcessType')
        recovery_target_config = cohesity_management_sdk.models_v2.recovery_target_config_5.RecoveryTargetConfig5.from_dictionary(dictionary.get('recoveryTargetConfig')) if dictionary.get('recoveryTargetConfig') else None
        rename_recovered_vms_params = cohesity_management_sdk.models_v2.recover_or_clone_vm_s_rename_config_params.RecoverOrCloneVMsRenameConfigparams.from_dictionary(
            dictionary.get('renameRecoveredVmsParams')) if dictionary.get('renameRecoveredVmsParams') else None
        vlan_config = cohesity_management_sdk.models_v2.vlan_config_1.VlanConfig1.from_dictionary(dictionary.get('vlanConfig')) if dictionary.get('vlanConfig') else None


        # Return an object of this model
        return cls(attempt_differential_restore,
                   rename_recovered_v_apps_params,
                   continue_on_error,
                   disk_provision_type,
                   enable_nbdssl_fallback,
                   leverage_san_transport,
                   power_on_vms,
                   recovery_process_type,
                   recovery_target_config,
                   rename_recovered_vms_params,
                   vlan_config)