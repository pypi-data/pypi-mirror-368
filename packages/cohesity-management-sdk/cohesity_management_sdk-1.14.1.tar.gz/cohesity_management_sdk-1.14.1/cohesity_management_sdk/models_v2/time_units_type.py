# -*- coding: utf-8 -*-


class TimeUnitsType(object):

    """Implementation of the 'Time Units type.' model.

    Time Units type.

    Attributes:
        time_units (TimeUnitsEnum): Specifies Time Units type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "time_units":'timeUnits'
    }

    def __init__(self,
                 time_units=None):
        """Constructor for the TimeUnitsType class"""

        # Initialize members of the class
        self.time_units = time_units


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
        time_units = dictionary.get('timeUnits')

        # Return an object of this model
        return cls(time_units)


