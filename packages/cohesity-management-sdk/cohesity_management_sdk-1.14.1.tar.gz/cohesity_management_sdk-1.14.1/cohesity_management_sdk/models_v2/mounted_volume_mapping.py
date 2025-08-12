# -*- coding: utf-8 -*-


class MountedVolumeMapping(object):

    """Implementation of the 'MountedVolumeMapping' model.

    Specifies the mapping of original volume and mounted volume after Instant
    Volume Mount.

    Attributes:
        original_volume (string): Specifies the name of the original volume.
        mounted_volume (string): Specifies the name of the point where the
            volume is mounted.
        file_system_type (string): Specifies the type of the file system of
            the volume.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "original_volume":'originalVolume',
        "mounted_volume":'mountedVolume',
        "file_system_type":'fileSystemType'
    }

    def __init__(self,
                 original_volume=None,
                 mounted_volume=None,
                 file_system_type=None):
        """Constructor for the MountedVolumeMapping class"""

        # Initialize members of the class
        self.original_volume = original_volume
        self.mounted_volume = mounted_volume
        self.file_system_type = file_system_type


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
        original_volume = dictionary.get('originalVolume')
        mounted_volume = dictionary.get('mountedVolume')
        file_system_type = dictionary.get('fileSystemType')

        # Return an object of this model
        return cls(original_volume,
                   mounted_volume,
                   file_system_type)


