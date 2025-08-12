# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.vmware_v_ms_recovery_target_config
import cohesity_management_sdk.models_v2.recover_or_clone_v_ms_rename_config_params
import cohesity_management_sdk.models_v2.vlan_config_1

class VmwareTargetParams1(object):

    """Implementation of the 'VmwareTargetParams1' model.

    Specifies the params for recovering to a VMware target.

    Attributes:
        attempt_differential_restore (bool): Specifies whether to attempt differential restore.
        continue_on_error (bool): Specifies whether to continue recovering other vms if one of
          vms failed to recover. Default value is false.
        disk_provision_type (DiskProvisionTYpeEnum): Specifies the Virtual Disk Provisioning Policies
            for Vmware VM
        enable_nbdssl_fallback (bool): If this field is set to true and SAN transport recovery fails,
          then recovery will fallback to use NBDSSL transport. This field only applies
          if 'leverageSanTransport' is set to true.
        is_multi_stage_restore (bool): Specifies whether this is a multistage restore which is used
          for migration/hot-standby purpose.
        leverage_san_transport (bool): Specifies whether to enable SAN transport for copy recovery or
          not
        overwrite_existing_vm (bool):Specifies whether to overwrite the VM at the target location.
          This is a data destructive operation and if this is selected, the original
          VM may no longer be accessible. This option is only applicable if renameRecoveredVmParams
          is null and powerOffAndRenameExistingVm is false. This option is not supported
          for vApp or vApp template recoveries. Default value is false.
        power_off_and_rename_existing_vm (bool): Specifies whether to power off and mark the VM at the target
          location as deprecated. As an example, <vm_name> will be renamed to deprecated::<vm_name>,
          and a new VM with the name <vm_name> in place of the now deprecated VM.
          Both deprecated::<vm_name> and <vm_name> will exist on the primary, but
          the corresponding protection job will only backup <vm_name> on its next
          run. Only applicable if renameRecoveredVmParams is null and overwriteExistingVm
          is false. This option is not supported for vApp or vApp template recoveries.
          Default value is false.
        power_on_vms (bool): Specifies whether to power on vms after recovery. If not specified,
          or false, recovered vms will be in powered off state.
        recovery_process_type (RecoveryProcessType1Enum): Specifies type of Recovery Process to be used. InstantRecovery/CopyRecovery
          etc... Default value is InstantRecovery.
        recovery_target_config (VmwareVmRecoveryTargetConfig): Specifies params to rename the VMs that are recovered. If not
          specified, the original names of the VMs are preserved.
        rename_recovered_vms_params (RecoveredOrClonedVmsRenameConfig): Specifies params to rename the VMs that are recovered. If not
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
        "continue_on_error":'continueOnError',
        "disk_provision_type":'diskProvisionType',
        "enable_nbdssl_fallback":'enableNBDSSLFallback',
        "is_multi_stage_restore":'isMultiStageRestore',
        "leverage_san_transport":'leverageSanTransport',
        "overwrite_existing_vm":'overwriteExistingVm',
        "power_off_and_rename_existing_vm":'powerOffAndRenameExistingVm',
        "power_on_vms":'powerOnVms',
        "recovery_process_type":'recoveryProcessType',
        "recovery_target_config":'recoveryTargetConfig',
        "rename_recovered_vms_params":'renameRecoveredVmsParams',
        "vlan_config":'vlanConfig'
    }

    def __init__(self,
                 attempt_differential_restore=None,
                 continue_on_error=None,
                 disk_provision_type=None,
                 enable_nbdssl_fallback=None,
                 is_multi_stage_restore=None,
                 leverage_san_transport=None,
                 overwrite_existing_vm=None,
                 power_off_and_rename_existing_vm=None,
                 power_on_vms=None,
                 recovery_process_type=None,
                 recovery_target_config=None,
                 rename_recovered_vms_params=None,
                 vlan_config=None
                 ):
        """Constructor for the VmwareTargetParams1 class"""

        # Initialize members of the class
        self.attempt_differential_restore = attempt_differential_restore
        self.continue_on_error = continue_on_error
        self.disk_provision_type = disk_provision_type
        self.enable_nbdssl_fallback = enable_nbdssl_fallback
        self.is_multi_stage_restore = is_multi_stage_restore
        self.leverage_san_transport = leverage_san_transport
        self.overwrite_existing_vm = overwrite_existing_vm
        self.power_off_and_rename_existing_vm = power_off_and_rename_existing_vm
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
        continue_on_error = dictionary.get('continueOnError')
        disk_provision_type = dictionary.get('diskProvisionType')
        enable_nbdssl_fallback = dictionary.get('enableNBDSSLFallback')
        is_multi_stage_restore = dictionary.get('isMultiStageRestore')
        leverage_san_transport = dictionary.get('leverageSanTransport')
        overwrite_existing_vm = dictionary.get('overwriteExistingVm')
        power_off_and_rename_existing_vm = dictionary.get('powerOffAndRenameExistingVm')
        power_on_vms = dictionary.get('powerOnVms')
        recovery_process_type = dictionary.get('recoveryProcessType')
        recovery_target_config = dictionary.get('recoveryTargetConfig')
        rename_recovered_vms_params = dictionary.get('renameRecoveredVmsParams')
        vlan_config = cohesity_management_sdk.models_v2.vlan_config_1.VlanConfig1.from_dictionary(dictionary.get('vlanConfig')) if dictionary.get('vlanConfig') else None


        # Return an object of this model
        return cls(attempt_differential_restore,
                   continue_on_error,
                   disk_provision_type,
                   enable_nbdssl_fallback,
                   is_multi_stage_restore,
                   leverage_san_transport,
                   overwrite_existing_vm,
                   power_off_and_rename_existing_vm,
                   power_on_vms,
                   recovery_process_type,
                   recovery_target_config,
                   rename_recovered_vms_params,
                   vlan_config)