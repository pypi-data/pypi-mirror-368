# -*- coding: utf-8 -*-


class ErasureCodingParameters(object):

    """Implementation of the 'ErasureCodingParameters.' model.

    Specifies parameters for erasure coding.

    Attributes:
        delay_secs (long|int): Specifies the time in seconds when erasure coding starts.
        enabled (bool): Specifies whether to enable erasure coding on a Storage Domain.
        inline_enabled (bool): Specifies whether inline erasure coding is enabled. This field
          is appliciable only if enabled is set to true.
        num_coded_stripes (long|int): Specifies the number of coded stripes.
        num_data_stripes (long|int): Specifies the number of data stripes.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "delay_secs":'delaySecs',
        "enabled":'enabled',
        "inline_enabled":'inlineEnabled',
        "num_coded_stripes":'numCodedStripes',
        "num_data_stripes":'numDataStripes'
    }

    def __init__(self,
                 delay_secs=None,
                 enabled=None,
                 inline_enabled=None,
                 num_coded_stripes=None,
                 num_data_stripes=None):
        """Constructor for the ErasureCodingParameters class"""

        # Initialize members of the class
        self.delay_secs = delay_secs
        self.enabled = enabled
        self.inline_enabled = inline_enabled
        self.num_coded_stripes = num_coded_stripes
        self.num_data_stripes = num_data_stripes


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
        delay_secs = dictionary.get('delaySecs')
        enabled = dictionary.get('enabled')
        inline_enabled = dictionary.get('inlineEnabled')
        num_coded_stripes = dictionary.get('numCodedStripes')
        num_data_stripes = dictionary.get('numDataStripes')

        # Return an object of this model
        return cls(delay_secs,
                   enabled,
                   inline_enabled,
                   num_coded_stripes,
                   num_data_stripes
                   )