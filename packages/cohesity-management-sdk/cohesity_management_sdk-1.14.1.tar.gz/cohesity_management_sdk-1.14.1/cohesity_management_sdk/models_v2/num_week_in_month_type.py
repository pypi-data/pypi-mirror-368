# -*- coding: utf-8 -*-


class NumWeekInMonthType(object):

    """Implementation of the 'Num Week In Month type.' model.

    Num Week In Month type.

    Attributes:
        num_week_in_month (NumWeekInMonthEnum): Specifies Num Week In Month
            type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "num_week_in_month":'numWeekInMonth'
    }

    def __init__(self,
                 num_week_in_month=None):
        """Constructor for the NumWeekInMonthType class"""

        # Initialize members of the class
        self.num_week_in_month = num_week_in_month


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
        num_week_in_month = dictionary.get('numWeekInMonth')

        # Return an object of this model
        return cls(num_week_in_month)


