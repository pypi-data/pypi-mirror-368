# -*- coding: utf-8 -*-


class GenericNasParams1(object):

    """Implementation of the 'GenericNasParams1' model.

    Specifies the parameters for GenericNas object.

    Attributes:
        supported_nas_mount_protocols (list of SupportedNasMountProtocolEnum):
            Specifies a list of NAS mount protocols supported by this object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "supported_nas_mount_protocols":'supportedNasMountProtocols'
    }

    def __init__(self,
                 supported_nas_mount_protocols=None):
        """Constructor for the GenericNasParams1 class"""

        # Initialize members of the class
        self.supported_nas_mount_protocols = supported_nas_mount_protocols


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

        # Return an object of this model
        return cls(supported_nas_mount_protocols)


