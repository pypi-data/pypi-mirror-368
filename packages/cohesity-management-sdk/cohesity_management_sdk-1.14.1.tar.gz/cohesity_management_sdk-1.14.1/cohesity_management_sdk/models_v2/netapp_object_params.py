# -*- coding: utf-8 -*-


class NetappObjectParams(object):

    """Implementation of the 'NetappObjectParams' model.

    Specifies the common parameters for Netapp objects.

    Attributes:
        supported_nas_mount_protocols (list of
            SupportedNasMountProtocol1Enum): Specifies a list of NAS mount
            protocols supported by this object.
        volume_extended_style (volumeExtendedStyle2Enum): Specifies the extended style of a NetApp volume.
        volume_type (VolumeType1Enum): Specifies the Netapp volume type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "supported_nas_mount_protocols":'supportedNasMountProtocols',
        "volume_extended_style":'volumeExtendedStyle',
        "volume_type":'volumeType'
    }

    def __init__(self,
                 supported_nas_mount_protocols=None,
                 volume_extended_style=None,
                 volume_type=None):
        """Constructor for the NetappObjectParams class"""

        # Initialize members of the class
        self.supported_nas_mount_protocols = supported_nas_mount_protocols
        self.volume_extended_style = volume_extended_style
        self.volume_type = volume_type


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
        supported_nas_mount_protocols = dictionary.get('supportedNasMountProtocols')
        volume_extended_style = dictionary.get('volumeExtendedStyle')
        volume_type = dictionary.get('volumeType')

        # Return an object of this model
        return cls(supported_nas_mount_protocols,
                   volume_extended_style,
                   volume_type)