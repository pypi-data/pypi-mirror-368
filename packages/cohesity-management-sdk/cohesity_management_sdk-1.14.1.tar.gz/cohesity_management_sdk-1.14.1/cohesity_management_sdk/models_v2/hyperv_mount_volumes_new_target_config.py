# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_target
import cohesity_management_sdk.models_v2.target_vm_credentials_10

class HypervMountVolumesNewTargetConfig(object):

    """Implementation of the 'HyperV Mount Volumes New Target Config.' model.

    Specifies the configuration for mounting volumes to a new target.

    Attributes:
        mount_target (RecoverTarget): Specifies the target entity to recover
            to.
        bring_disks_online (bool): Specifies whether the volumes need to be
            online within the target environment after attaching the disks.
            For linux VMs, this should always be set to false because bring
            disks online is only supported for Windows VM. If this is set to
            true, HyperV Integration Services must be installed on the VM.
        target_vm_credentials (TargetVmCredentials10): Specifies credentials
            to access the target VM.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mount_target":'mountTarget',
        "bring_disks_online":'bringDisksOnline',
        "target_vm_credentials":'targetVmCredentials'
    }

    def __init__(self,
                 mount_target=None,
                 bring_disks_online=None,
                 target_vm_credentials=None):
        """Constructor for the HypervMountVolumesNewTargetConfig class"""

        # Initialize members of the class
        self.mount_target = mount_target
        self.bring_disks_online = bring_disks_online
        self.target_vm_credentials = target_vm_credentials


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
        mount_target = cohesity_management_sdk.models_v2.recover_target.RecoverTarget.from_dictionary(dictionary.get('mountTarget')) if dictionary.get('mountTarget') else None
        bring_disks_online = dictionary.get('bringDisksOnline')
        target_vm_credentials = cohesity_management_sdk.models_v2.target_vm_credentials_10.TargetVmCredentials10.from_dictionary(dictionary.get('targetVmCredentials')) if dictionary.get('targetVmCredentials') else None

        # Return an object of this model
        return cls(mount_target,
                   bring_disks_online,
                   target_vm_credentials)


