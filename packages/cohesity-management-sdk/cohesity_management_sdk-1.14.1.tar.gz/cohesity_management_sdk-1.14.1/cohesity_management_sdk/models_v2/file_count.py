# -*- coding: utf-8 -*-
# Copyright 2022 Cohesity Inc.


class FileCount(object):

    """Implementation of the 'FileCount' model.

    Specifies the number of files with provided size range.

    Attributes:
        lower_size_bytes (long|int): Specifies the lower bound of file size in
            bytes. This value is inclusive.
        upper_size_bytes (long|int): Specifies the upper bound of file size in
            bytes. This value is inclusive.
        count (long|int): Specifies the number of files with size in this
            range.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "lower_size_bytes":'lowerSizeBytes',
        "upper_size_bytes":'upperSizeBytes',
        "count":'count'
    }

    def __init__(self,
                 lower_size_bytes=None,
                 upper_size_bytes=None,
                 count=None):
        """Constructor for the FileCount class"""

        # Initialize members of the class
        self.lower_size_bytes = lower_size_bytes
        self.upper_size_bytes = upper_size_bytes
        self.count = count


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
        lower_size_bytes = dictionary.get('lowerSizeBytes')
        upper_size_bytes = dictionary.get('upperSizeBytes')
        count = dictionary.get('count')

        # Return an object of this model
        return cls(lower_size_bytes,
                   upper_size_bytes,
                   count)


