# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.mount_target
import cohesity_management_sdk.models_v2.recover_volume_mapping
import cohesity_management_sdk.models_v2.vlan_config_1

class PhysicalRecoveryTargetParams1(object):

    """Implementation of the 'Physical Recovery Target Params1' model.

    Specifies the parameters for a physical recovery target.

    Attributes:
        mount_target (MountTarget): Specifies the target entity where the
            volumes are being mounted.
        volume_mapping (list of RecoverVolumeMapping): Specifies the mapping
            from source volumes to destination volumes.
        force_unmount_volume (bool): Specifies whether volume would be
            dismounted first during LockVolume failure. If not specified,
            default is false.
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
        "mount_target":'mountTarget',
        "volume_mapping":'volumeMapping',
        "force_unmount_volume":'forceUnmountVolume',
        "vlan_config":'vlanConfig'
    }

    def __init__(self,
                 mount_target=None,
                 volume_mapping=None,
                 force_unmount_volume=None,
                 vlan_config=None):
        """Constructor for the PhysicalRecoveryTargetParams1 class"""

        # Initialize members of the class
        self.mount_target = mount_target
        self.volume_mapping = volume_mapping
        self.force_unmount_volume = force_unmount_volume
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
        mount_target = cohesity_management_sdk.models_v2.mount_target.MountTarget.from_dictionary(dictionary.get('mountTarget')) if dictionary.get('mountTarget') else None
        volume_mapping = None
        if dictionary.get("volumeMapping") is not None:
            volume_mapping = list()
            for structure in dictionary.get('volumeMapping'):
                volume_mapping.append(cohesity_management_sdk.models_v2.recover_volume_mapping.RecoverVolumeMapping.from_dictionary(structure))
        force_unmount_volume = dictionary.get('forceUnmountVolume')
        vlan_config = cohesity_management_sdk.models_v2.vlan_config_1.VlanConfig1.from_dictionary(dictionary.get('vlanConfig')) if dictionary.get('vlanConfig') else None

        # Return an object of this model
        return cls(mount_target,
                   volume_mapping,
                   force_unmount_volume,
                   vlan_config)


