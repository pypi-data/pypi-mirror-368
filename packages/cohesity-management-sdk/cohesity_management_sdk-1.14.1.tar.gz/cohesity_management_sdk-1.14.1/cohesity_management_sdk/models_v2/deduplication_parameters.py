# -*- coding: utf-8 -*-

class DeduplicationParameters(object):

    """Implementation of the 'DeduplicationParams' model.

    Specifies parameters for deduplication.

    Attributes:
        inline_enabled (bool): Specifies if inline deduplication is enabled. This field is appliciable
          only if deduplicationEnabled is set to true.
        enabled (bool): Specifies whether deduplication is enabled on this Storage Domain.
          If enabled, cohesity cluster will eliminate duplicate blocks and thus reducing
          the amount of storage space.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "inline_enabled":'inlineEnabled',
        "enabled":'enabled'
    }

    def __init__(self,
                 inline_enabled=None,
                 enabled=None
                 ):
        """Constructor for the DeduplicationParameters class"""

        # Initialize members of the class
        self.inline_enabled = inline_enabled
        self.enabled = enabled

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
        enabled = dictionary.get('enabled')


        # Return an object of this model
        return cls(inline_enabled,
                   enabled)