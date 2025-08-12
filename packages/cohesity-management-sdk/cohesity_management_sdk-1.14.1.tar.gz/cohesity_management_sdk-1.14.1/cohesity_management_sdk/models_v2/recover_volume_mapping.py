# -*- coding: utf-8 -*-


class RecoverVolumeMapping(object):

    """Implementation of the 'Recover Volume Mapping' model.

    Specifies the mapping from a source volume to a destination volume.

    Attributes:
        source_volume_guid (string): Specifies the guid of the source volume.
        destination_volume_guid (string): Specifies the guid of the
            destination volume.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_volume_guid":'sourceVolumeGuid',
        "destination_volume_guid":'destinationVolumeGuid'
    }

    def __init__(self,
                 source_volume_guid=None,
                 destination_volume_guid=None):
        """Constructor for the RecoverVolumeMapping class"""

        # Initialize members of the class
        self.source_volume_guid = source_volume_guid
        self.destination_volume_guid = destination_volume_guid


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
        source_volume_guid = dictionary.get('sourceVolumeGuid')
        destination_volume_guid = dictionary.get('destinationVolumeGuid')

        # Return an object of this model
        return cls(source_volume_guid,
                   destination_volume_guid)


