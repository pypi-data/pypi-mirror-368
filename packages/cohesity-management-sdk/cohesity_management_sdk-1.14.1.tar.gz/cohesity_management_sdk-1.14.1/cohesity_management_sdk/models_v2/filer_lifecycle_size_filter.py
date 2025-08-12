# -*- coding: utf-8 -*-


class FilerLifecycleSizeFilter(object):

    """Implementation of the 'FilerLifecycleSizeFilter' model.

    Specifies the Lifecycle Size Filter information with minimum and
      maximum values.

    Attributes:
        max_bytes (long|int64): Specifies the maximum size in bytes.
        min_bytes (long|int64): Specifies the minimum size in bytes.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "max_bytes":'maxBytes',
        "min_bytes":'minBytes'
    }

    def __init__(self,
                 max_bytes=None,
                 min_bytes=None):
        """Constructor for the FilerLifecycleSizeFilter class"""

        # Initialize members of the class
        self.max_bytes = max_bytes
        self.min_bytes = min_bytes


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
        max_bytes = dictionary.get('maxBytes')
        min_bytes = dictionary.get('minBytes')

        # Return an object of this model
        return cls(max_bytes,
                   min_bytes)