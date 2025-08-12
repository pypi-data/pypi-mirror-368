# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vmware_recover_disks_original_source_config
import cohesity_management_sdk.models_v2.vmware_recover_disks_target_source_config
import cohesity_management_sdk.models_v2.vlan_config_1

class VmwareTargetParams7(object):

    """Implementation of the 'VMware Target Params.7' model.

    Specifies the parameters for a VMware recovery target.

    Attributes:
        original_source_config (VmwareRecoverDisksOriginalSourceConfig):
            Specifies the configuration for restoring a disk to the original
            VM from which the snapshot was taken.
        target_source_config (VmwareRecoverDisksTargetSourceConfig): Specifies
            the configuration for restoring disks to a different VM than the
            one from which the snapshot was taken.
        vlan_config (VlanConfig1): Specifies VLAN Params associated with the
            recovered. If this is not specified, then the VLAN settings will
            be automatically selected from one of the below options: a. If
            VLANs are configured on Cohesity, then the VLAN host/VIP will be
            automatically based on the client's (e.g. ESXI host) IP address.
            b. If VLANs are not configured on Cohesity, then the partition
            hostname or VIPs will be used for Recovery.
        power_off_vms (bool): Specifies whether or not to power off VMs before
            performing the recovery.
        power_on_vms (bool): Specifies whether or not to power on VMs after
            performing the recovery.
        continue_on_error (bool): Specifies whether or not to continue
            performing the recovery in the event that an error is
            encountered.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "original_source_config":'originalSourceConfig',
        "target_source_config":'targetSourceConfig',
        "vlan_config":'vlanConfig',
        "power_off_vms":'powerOffVms',
        "power_on_vms":'powerOnVms',
        "continue_on_error":'continueOnError'
    }

    def __init__(self,
                 original_source_config=None,
                 target_source_config=None,
                 vlan_config=None,
                 power_off_vms=None,
                 power_on_vms=None,
                 continue_on_error=None):
        """Constructor for the VmwareTargetParams7 class"""

        # Initialize members of the class
        self.original_source_config = original_source_config
        self.target_source_config = target_source_config
        self.vlan_config = vlan_config
        self.power_off_vms = power_off_vms
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
        original_source_config = cohesity_management_sdk.models_v2.vmware_recover_disks_original_source_config.VmwareRecoverDisksOriginalSourceConfig.from_dictionary(dictionary.get('originalSourceConfig')) if dictionary.get('originalSourceConfig') else None
        target_source_config = cohesity_management_sdk.models_v2.vmware_recover_disks_target_source_config.VmwareRecoverDisksTargetSourceConfig.from_dictionary(dictionary.get('targetSourceConfig')) if dictionary.get('targetSourceConfig') else None
        vlan_config = cohesity_management_sdk.models_v2.vlan_config_1.VlanConfig1.from_dictionary(dictionary.get('vlanConfig')) if dictionary.get('vlanConfig') else None
        power_off_vms = dictionary.get('powerOffVms')
        power_on_vms = dictionary.get('powerOnVms')
        continue_on_error = dictionary.get('continueOnError')

        # Return an object of this model
        return cls(original_source_config,
                   target_source_config,
                   vlan_config,
                   power_off_vms,
                   power_on_vms,
                   continue_on_error)


