# -*- coding: utf-8 -*-


class BgpTimers(object):

    """Implementation of the 'BgpTimers' model.

    BGP protocol timers.

    Attributes:
        keep_alive (int): Keep alive interval in seconds.
        hold_time (int): Hold time in seconds.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "keep_alive":'keepAlive',
        "hold_time":'holdTime'
    }

    def __init__(self,
                 keep_alive=None,
                 hold_time=None):
        """Constructor for the BgpTimers class"""

        # Initialize members of the class
        self.keep_alive = keep_alive
        self.hold_time = hold_time


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
        keep_alive = dictionary.get('keepAlive')
        hold_time = dictionary.get('holdTime')

        # Return an object of this model
        return cls(keep_alive,
                   hold_time)


