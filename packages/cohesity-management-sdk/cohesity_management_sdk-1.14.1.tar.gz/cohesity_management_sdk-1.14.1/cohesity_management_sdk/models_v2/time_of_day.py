# -*- coding: utf-8 -*-


class TimeOfDay(object):

    """Implementation of the 'TimeOfDay' model.

    Specifies the time of day. Used for scheduling purposes.

    Attributes:
        hour (int): Specifies the hour of the day (0-23).
        minute (int): Specifies the minute of the hour (0-59).
        time_zone (string): Specifies the time zone of the user. If not
            specified, default value is assumed as America/Los_Angeles.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "hour":'hour',
        "minute":'minute',
        "time_zone":'timeZone'
    }

    def __init__(self,
                 hour=None,
                 minute=None,
                 time_zone='America/Los_Angeles'):
        """Constructor for the TimeOfDay class"""

        # Initialize members of the class
        self.hour = hour
        self.minute = minute
        self.time_zone = time_zone


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
        time_zone = dictionary.get("timeZone") if dictionary.get("timeZone") else 'America/Los_Angeles'

        # Return an object of this model
        return cls(hour,
                   minute,
                   time_zone)


