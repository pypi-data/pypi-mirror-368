# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vmware_recover_target_source_disk_params

class VmwareRecoverDisksTargetSourceConfig(object):

    """Implementation of the 'VmwareRecoverDisksTargetSourceConfig' model.

    Specifies the configuration for restoring disks to a different VM than the
    one from which the snapshot was taken.

    Attributes:
        source_id (long|int): Specifies the source ID of the VM to which the
            disks will be restored.
        disks (list of VmwareRecoverTargetSourceDiskParams): Specifies the
            disks to be recovered and the location to which they will be
            recovered.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_id":'sourceId',
        "disks":'disks'
    }

    def __init__(self,
                 source_id=None,
                 disks=None):
        """Constructor for the VmwareRecoverDisksTargetSourceConfig class"""

        # Initialize members of the class
        self.source_id = source_id
        self.disks = disks


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
        source_id = dictionary.get('sourceId')
        disks = None
        if dictionary.get("disks") is not None:
            disks = list()
            for structure in dictionary.get('disks'):
                disks.append(cohesity_management_sdk.models_v2.vmware_recover_target_source_disk_params.VmwareRecoverTargetSourceDiskParams.from_dictionary(structure))

        # Return an object of this model
        return cls(source_id,
                   disks)


