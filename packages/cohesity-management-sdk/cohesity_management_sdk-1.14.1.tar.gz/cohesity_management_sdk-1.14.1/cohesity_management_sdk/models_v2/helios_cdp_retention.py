# -*- coding: utf-8 -*-


class HeliosCdpRetention(object):

    """Implementation of the 'HeliosCdpRetention' model.

    Specifies the retention of a CDP backup.

    Attributes:
        unit (Unit7Enum): Specificies the Retention Unit of a CDP backup
            measured in minutes or hours.
        duration (int): Specifies the duration for a cdp backup retention.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "unit":'unit',
        "duration":'duration'
    }

    def __init__(self,
                 unit=None,
                 duration=None):
        """Constructor for the HeliosCdpRetention class"""

        # Initialize members of the class
        self.unit = unit
        self.duration = duration


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
        unit = dictionary.get('unit')
        duration = dictionary.get('duration')

        # Return an object of this model
        return cls(unit,
                   duration)


