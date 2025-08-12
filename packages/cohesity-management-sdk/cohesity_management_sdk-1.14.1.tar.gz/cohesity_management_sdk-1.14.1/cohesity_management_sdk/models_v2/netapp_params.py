# -*- coding: utf-8 -*-


class NetappParams(object):

    """Implementation of the 'NetappParams' model.

    Specifies the parameters specific to NetApp type snapshot.

    Attributes:
        supported_nas_mount_protocols (list of
            SupportedNasMountProtocol1Enum): Specifies a list of NAS mount
            protocols supported by this object.
        volume_type (VolumeType1Enum): Specifies the Netapp volume type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "supported_nas_mount_protocols":'supportedNasMountProtocols',
        "volume_type":'volumeType'
    }

    def __init__(self,
                 supported_nas_mount_protocols=None,
                 volume_type=None):
        """Constructor for the NetappParams class"""

        # Initialize members of the class
        self.supported_nas_mount_protocols = supported_nas_mount_protocols
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
        volume_type = dictionary.get('volumeType')

        # Return an object of this model
        return cls(supported_nas_mount_protocols,
                   volume_type)


