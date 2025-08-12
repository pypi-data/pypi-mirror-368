# -*- coding: utf-8 -*-


class YearSchedule1(object):

    """Implementation of the 'Year Schedule' model.

    Specifies settings that define a schedule for a Protection Group
      to run on specific year and specific day of that year.

    Attributes:
        day_of_year (DayOfYearEnum): Specifies the day of the Year (such as ''First'' or ''Last'')
          in a Yearly Schedule. <br>This field is used to define the day in the year
          to start the Protection Group Run. <br> Example: if ''dayOfYear'' is set
          to ''First'', a backup is performed on the first day of every year. <br>
          Example: if ''dayOfYear'' is set to ''Last'', a backup is performed on the
          last day of every year

    """

    # Create a mapping from Model property na.mes to API property names
    _names = {
        "day_of_year":'dayOfYear'
    }

    def __init__(self,
                 day_of_year=None):
        """Constructor for the YearSchedule class"""

        # Initialize members of the class
        self.day_of_year = day_of_year


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
        day_of_year = dictionary.get('dayOfYear')

        # Return an object of this model
        return cls(day_of_year)