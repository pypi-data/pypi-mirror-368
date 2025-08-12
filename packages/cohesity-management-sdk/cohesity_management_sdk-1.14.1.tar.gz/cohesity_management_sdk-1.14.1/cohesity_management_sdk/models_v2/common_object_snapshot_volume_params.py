# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.volume_info

class CommonObjectSnapshotVolumeParams(object):

    """Implementation of the 'CommonObjectSnapshotVolumeParams' model.

    Specifies volume info of snapshot across all enviroments.

    Attributes:
        volumes (list of VolumeInfo): Specifies a list of volume info.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "volumes":'volumes'
    }

    def __init__(self,
                 volumes=None):
        """Constructor for the CommonObjectSnapshotVolumeParams class"""

        # Initialize members of the class
        self.volumes = volumes


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
        volumes = None
        if dictionary.get("volumes") is not None:
            volumes = list()
            for structure in dictionary.get('volumes'):
                volumes.append(cohesity_management_sdk.models_v2.volume_info.VolumeInfo.from_dictionary(structure))

        # Return an object of this model
        return cls(volumes)


