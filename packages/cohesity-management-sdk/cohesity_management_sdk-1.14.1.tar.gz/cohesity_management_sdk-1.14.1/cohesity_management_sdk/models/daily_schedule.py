# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class DailySchedule(object):

    """Implementation of the 'DailySchedule' model.

    Specifies a daily or weekly backup schedule.

    Attributes:
        days (list of DayEnum): Array of Days.  Specifies a list of days of
            the week when to start Job Runs. If no days are specified, the
            Jobs Runs will run every day of the week. Specifies a day in a
            week such as 'kSunday', 'kMonday', etc.
        frequency (long|int): Specifies a factor to multiply the unit by, to
          determine the copy schedule. For example if set to 2 and the
          unit is hourly, then Snapshots from the first eligible Job
          Run for every 2 hour period is copied. Only applies to Minutes,
          Hours and Days

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "days":'days',
        "frequency": 'frequency'
    }

    def __init__(self,
                 days=None,
                 frequency=None):
        """Constructor for the DailySchedule class"""

        # Initialize members of the class
        self.days = days
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
        days = dictionary.get('days')
        frequency = dictionary.get('frequency')

        # Return an object of this model
        return cls(days, frequency)


