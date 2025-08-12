# -*- coding: utf-8 -*-

class CompressionParams(object):

    """Implementation of the 'CompressionParams' model.

    Specifies parameters for compression.

    Attributes:
        inline_enabled (bool): Specifies whether inline compression is enabled. This field is
          appliciable only if inlineDeduplicationEnabled is set to true and compression
          is enabled.
        type (Type73Enum): Specifies copmpression type for a Storage Domain.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "inline_enabled":'inlineEnabled',
        "mtype":'type'
    }

    def __init__(self,
                 inline_enabled=None,
                 mtype=None
                 ):
        """Constructor for the CompressionParams class"""

        # Initialize members of the class
        self.inline_enabled = inline_enabled
        self.mtype = mtype

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
        inline_enabled = dictionary.get('inlineEnabled')
        mtype = dictionary.get('type')


        # Return an object of this model
        return cls(inline_enabled,
                   mtype)