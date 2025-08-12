# -*- coding: utf-8 -*-


class Time(object):

    """Implementation of the 'Time' model.

    Specifies the time in hours and minutes.

    Attributes:
        hour (long|int): Specifies the hour of this time.
        minute (long|int): Specifies the minute of this time.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "hour":'hour',
        "minute":'minute'
    }

    def __init__(self,
                 hour=None,
                 minute=None
                 ):
        """Constructor for the Time class"""

        # Initialize members of the class
        self.hour = hour
        self.minute = minute



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
        hour = dictionary.get('hour')
        minute = dictionary.get('minute')

        # Return an object of this model
        return cls(hour,
                   minute)