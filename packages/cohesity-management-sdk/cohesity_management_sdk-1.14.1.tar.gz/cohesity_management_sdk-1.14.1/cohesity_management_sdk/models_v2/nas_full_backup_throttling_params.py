# -*- coding: utf-8 -*-


class NASFullBackupThrottlingParams(object):

    """Implementation of the 'NAS Full Backup Throttling Params' model.

    Specifies the throttling configuration during full backup run.

    Attributes:
        max_metadata_fetch_percentage (int): Specifies the percentage value of
            maximum concurrent metadata to be fetched during full backup of
            the source.
        max_read_write_percentage (int): Specifies the percentage value of
            maximum concurrent read/write during full backup of the source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "max_metadata_fetch_percentage":'maxMetadataFetchPercentage',
        "max_read_write_percentage":'maxReadWritePercentage'
    }

    def __init__(self,
                 max_metadata_fetch_percentage=None,
                 max_read_write_percentage=None):
        """Constructor for the NASFullBackupThrottlingParams class"""

        # Initialize members of the class
        self.max_metadata_fetch_percentage = max_metadata_fetch_percentage
        self.max_read_write_percentage = max_read_write_percentage


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
        max_metadata_fetch_percentage = dictionary.get('maxMetadataFetchPercentage')
        max_read_write_percentage = dictionary.get('maxReadWritePercentage')

        # Return an object of this model
        return cls(max_metadata_fetch_percentage,
                   max_read_write_percentage)


