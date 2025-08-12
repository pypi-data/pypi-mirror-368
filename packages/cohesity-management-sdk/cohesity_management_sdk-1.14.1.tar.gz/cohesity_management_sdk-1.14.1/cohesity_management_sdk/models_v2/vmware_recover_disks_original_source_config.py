# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vmware_recover_original_source_disk_params

class VmwareRecoverDisksOriginalSourceConfig(object):

    """Implementation of the 'VmwareRecoverDisksOriginalSourceConfig' model.

    Specifies the configuration for restoring a disk to the original VM from
    which the snapshot was taken.

    Attributes:
        disks (list of VmwareRecoverOriginalSourceDiskParams): Specifies the
            disks to be recovered and the location to which they will be
            recovered.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "disks":'disks'
    }

    def __init__(self,
                 disks=None):
        """Constructor for the VmwareRecoverDisksOriginalSourceConfig class"""

        # Initialize members of the class
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
        disks = None
        if dictionary.get("disks") is not None:
            disks = list()
            for structure in dictionary.get('disks'):
                disks.append(cohesity_management_sdk.models_v2.vmware_recover_original_source_disk_params.VmwareRecoverOriginalSourceDiskParams.from_dictionary(structure))

        # Return an object of this model
        return cls(disks)


