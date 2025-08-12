# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.rename_recovered_vms_params
import cohesity_management_sdk.models_v2.rename_recovered_v_app_template_params
import cohesity_management_sdk.models_v2.recovery_target_config_6
import cohesity_management_sdk.models_v2.vlan_config_1

class VmwareTargetParams4(object):

    """Implementation of the 'VmwareTargetParams4' model.

    Specifies the params for recovering to a VMware target.

    Attributes:
        attempt_differential_restore (bool): Specifies whether to attempt differential restore.
        disk_provision_type (DiskProvisionTYpeEnum): Specifies the Virtual Disk Provisioning Policies
            for Vmware VM
        enable_nbdssl_fallback (bool): If this field is set to true and SAN transport recovery fails,
          then recovery will fallback to use NBDSSL transport. This field only applies
          if 'leverageSanTransport' is set to true.
        leverage_san_transport (bool): Specifies whether to enable SAN transport for copy recovery or
          not
        rename_recovered_vms_params (RenameRecoveredVmsParams): Specifies
            params to rename the VMs that are recovered. If not specified, the
            original names of the VMs are preserved.
        rename_recovered_v_app_template_params
            (RenameRecoveredVAppTemplateParams): Specifies params to rename
            the vApps templates that are recovered. If not specified, the
            original names of the vApp templates are preserved.
        recovery_target_config (RecoveryTargetConfig6): Specifies the recovery
            target configuration if recovery has to be done to a different
            location which is different from original source or to original
            Source with different configuration. If not specified, then the
            recovery of the vApp templates will be performed to original
            location with all configuration parameters retained.
        vlan_config (VlanConfig1): Specifies VLAN Params associated with the
            recovered. If this is not specified, then the VLAN settings will
            be automatically selected from one of the below options: a. If
            VLANs are configured on Cohesity, then the VLAN host/VIP will be
            automatically based on the client's (e.g. ESXI host) IP address.
            b. If VLANs are not configured on Cohesity, then the partition
            hostname or VIPs will be used for Recovery.
        continue_on_error (bool): Specifies whether to continue recovering
            other vms if one of vms failed to recover. Default value is
            false.
        recovery_process_type (RecoveryProcessType1Enum): Specifies type of
            Recovery Process to be used. InstantRecovery/CopyRecovery etc...
            Default value is InstantRecovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "attempt_differential_restore":'attemptDifferentialRestore',
        "disk_provision_type":'diskProvisionType',
        "enable_nbdssl_fallback":'enableNBDSSLFallback',
        "leverage_san_transport":'leverageSanTransport',
        "rename_recovered_vms_params":'renameRecoveredVmsParams',
        "rename_recovered_v_app_template_params":'renameRecoveredVAppTemplateParams',
        "recovery_target_config":'recoveryTargetConfig',
        "vlan_config":'vlanConfig',
        "continue_on_error":'continueOnError',
        "recovery_process_type":'recoveryProcessType'
    }

    def __init__(self,
                 attempt_differential_restore=None,
                 disk_provision_type=None,
                 enable_nbdssl_fallback=None,
                 leverage_san_transport=None,
                 rename_recovered_vms_params=None,
                 rename_recovered_v_app_template_params=None,
                 recovery_target_config=None,
                 vlan_config=None,
                 continue_on_error=None,
                 recovery_process_type=None):
        """Constructor for the VmwareTargetParams4 class"""

        # Initialize members of the class
        self.attempt_differential_restore = attempt_differential_restore
        self.disk_provision_type = disk_provision_type
        self.enable_nbdssl_fallback = enable_nbdssl_fallback
        self.leverage_san_transport = leverage_san_transport
        self.rename_recovered_vms_params = rename_recovered_vms_params
        self.rename_recovered_v_app_template_params = rename_recovered_v_app_template_params
        self.recovery_target_config = recovery_target_config
        self.vlan_config = vlan_config
        self.continue_on_error = continue_on_error
        self.recovery_process_type = recovery_process_type


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
        disk_provision_type = dictionary.get('diskProvisionType')
        enable_nbdssl_fallback = dictionary.get('enableNBDSSLFallback')
        leverage_san_transport = dictionary.get('leverageSanTransport')
        rename_recovered_vms_params = cohesity_management_sdk.models_v2.rename_recovered_vms_params.RenameRecoveredVmsParams.from_dictionary(dictionary.get('renameRecoveredVmsParams')) if dictionary.get('renameRecoveredVmsParams') else None
        rename_recovered_v_app_template_params = cohesity_management_sdk.models_v2.rename_recovered_v_app_template_params.RenameRecoveredVAppTemplateParams.from_dictionary(dictionary.get('renameRecoveredVAppTemplateParams')) if dictionary.get('renameRecoveredVAppTemplateParams') else None
        recovery_target_config = cohesity_management_sdk.models_v2.recovery_target_config_6.RecoveryTargetConfig6.from_dictionary(dictionary.get('recoveryTargetConfig')) if dictionary.get('recoveryTargetConfig') else None
        vlan_config = cohesity_management_sdk.models_v2.vlan_config_1.VlanConfig1.from_dictionary(dictionary.get('vlanConfig')) if dictionary.get('vlanConfig') else None
        continue_on_error = dictionary.get('continueOnError')
        recovery_process_type = dictionary.get('recoveryProcessType')

        # Return an object of this model
        return cls(attempt_differential_restore,
                   disk_provision_type,
                   enable_nbdssl_fallback,
                   leverage_san_transport,
                   rename_recovered_vms_params,
                   rename_recovered_v_app_template_params,
                   recovery_target_config,
                   vlan_config,
                   continue_on_error,
                   recovery_process_type)