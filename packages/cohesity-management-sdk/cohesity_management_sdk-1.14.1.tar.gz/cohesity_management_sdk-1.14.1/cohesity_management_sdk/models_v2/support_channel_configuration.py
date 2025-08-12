# -*- coding: utf-8 -*-


class SupportChannelConfiguration(object):

    """Implementation of the 'Support channel configuration.' model.

    Specifies the support channel configuration.

    Attributes:
        is_enabled (bool): Specifies id the support channel is enabled.
        end_time_usecs (long|int): Specifies the support channel expiry time.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "is_enabled":'isEnabled',
        "end_time_usecs":'endTimeUsecs'
    }

    def __init__(self,
                 is_enabled=None,
                 end_time_usecs=None):
        """Constructor for the SupportChannelConfiguration class"""

        # Initialize members of the class
        self.is_enabled = is_enabled
        self.end_time_usecs = end_time_usecs


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
        is_enabled = dictionary.get('isEnabled')
        end_time_usecs = dictionary.get('endTimeUsecs')

        # Return an object of this model
        return cls(is_enabled,
                   end_time_usecs)


