# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.original_target_config_5
import cohesity_management_sdk.models_v2.new_target_config_5
import cohesity_management_sdk.models_v2.mounted_volume_mapping
import cohesity_management_sdk.models_v2.vlan_config_1

class PhysicalRecoveryTargetParams(object):

    """Implementation of the 'Physical Recovery Target Params' model.

    Specifies the parameters for a physical recovery target.

    Attributes:
        mount_to_original_target (bool): Specifies whether to mount to the
            original target. If true, originalTargetConfig must be specified.
            If false, newTargetConfig must be specified.
        original_target_config (OriginalTargetConfig5): Specifies the
            configuration for mounting to the original target.
        new_target_config (NewTargetConfig5): Specifies the configuration for
            mounting to a new target.
        read_only_mount (bool): Specifies whether to perform a read-only
            mount. Default is false.
        volume_names (list of string): Specifies the names of volumes that
            need to be mounted. If this is not specified then all volumes that
            are part of the source VM will be mounted on the target VM.
        mounted_volume_mapping (list of MountedVolumeMapping): Specifies the
            mapping of original volumes and mounted volumes
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
        "mount_to_original_target":'mountToOriginalTarget',
        "original_target_config":'originalTargetConfig',
        "new_target_config":'newTargetConfig',
        "read_only_mount":'readOnlyMount',
        "volume_names":'volumeNames',
        "mounted_volume_mapping":'mountedVolumeMapping',
        "vlan_config":'vlanConfig'
    }

    def __init__(self,
                 mount_to_original_target=None,
                 original_target_config=None,
                 new_target_config=None,
                 read_only_mount=None,
                 volume_names=None,
                 mounted_volume_mapping=None,
                 vlan_config=None):
        """Constructor for the PhysicalRecoveryTargetParams class"""

        # Initialize members of the class
        self.mount_to_original_target = mount_to_original_target
        self.original_target_config = original_target_config
        self.new_target_config = new_target_config
        self.read_only_mount = read_only_mount
        self.volume_names = volume_names
        self.mounted_volume_mapping = mounted_volume_mapping
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
        mount_to_original_target = dictionary.get('mountToOriginalTarget')
        original_target_config = cohesity_management_sdk.models_v2.original_target_config_5.OriginalTargetConfig5.from_dictionary(dictionary.get('originalTargetConfig')) if dictionary.get('originalTargetConfig') else None
        new_target_config = cohesity_management_sdk.models_v2.new_target_config_5.NewTargetConfig5.from_dictionary(dictionary.get('newTargetConfig')) if dictionary.get('newTargetConfig') else None
        read_only_mount = dictionary.get('readOnlyMount')
        volume_names = dictionary.get('volumeNames')
        mounted_volume_mapping = None
        if dictionary.get("mountedVolumeMapping") is not None:
            mounted_volume_mapping = list()
            for structure in dictionary.get('mountedVolumeMapping'):
                mounted_volume_mapping.append(cohesity_management_sdk.models_v2.mounted_volume_mapping.MountedVolumeMapping.from_dictionary(structure))
        vlan_config = cohesity_management_sdk.models_v2.vlan_config_1.VlanConfig1.from_dictionary(dictionary.get('vlanConfig')) if dictionary.get('vlanConfig') else None

        # Return an object of this model
        return cls(mount_to_original_target,
                   original_target_config,
                   new_target_config,
                   read_only_mount,
                   volume_names,
                   mounted_volume_mapping,
                   vlan_config)


