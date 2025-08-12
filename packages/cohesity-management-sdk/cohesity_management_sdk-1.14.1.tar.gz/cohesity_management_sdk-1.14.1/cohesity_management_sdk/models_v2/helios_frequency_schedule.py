# -*- coding: utf-8 -*-


class HeliosFrequencySchedule(object):

    """Implementation of the 'HeliosFrequencySchedule' model.

    Specifies settings that define a daily schedule for a Protection Policy.

    Attributes:
        frequency (long|int): Specifies a factor to multiply the unit by, to
            determine the backup schedule. <br> Example: If 'frequency' set to
            2 and the unit is 'Hours', then Snapshots are backed up every 2
            hours. If selected unit is 'Weeks' or 'Months' then frequency will
            only be applied if policy type is DMaas.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "frequency":'frequency'
    }

    def __init__(self,
                 frequency=None):
        """Constructor for the HeliosFrequencySchedule class"""

        # Initialize members of the class
        self.frequency = frequency


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
        frequency = dictionary.get('frequency')

        # Return an object of this model
        return cls(frequency)


