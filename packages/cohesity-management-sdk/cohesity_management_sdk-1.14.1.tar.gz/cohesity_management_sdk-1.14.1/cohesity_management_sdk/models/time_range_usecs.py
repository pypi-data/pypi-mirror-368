# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class TimeRangeUsecs(object):

    """Implementation of the 'TimeRangeUsecs' model.

    IP Range for range of vip address addition.

    Attributes:
        end_time_usecs (long| int): The end time in usecs. A negative value here
            should be treated as an indefinite time range.
        start_time_usecs (long| int): The start time in usecs.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "end_time_usecs": 'endTimeUsecs',
        "start_time_usecs": 'startTimeUsecs'
    }

    def __init__(self,
                 end_time_usecs=None,
                 start_time_usecs=None):
        """Constructor for the TimeRangeUsecs class"""

        # Initialize members of the class
        self.end_time_usecs = end_time_usecs
        self.start_time_usecs = start_time_usecs


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
        end_time_usecs = dictionary.get('endTimeUsecs', None)
        start_time_usecs = dictionary.get('startTimeUsecs', None)

        # Return an object of this model
        return cls(end_time_usecs,
                   start_time_usecs)


