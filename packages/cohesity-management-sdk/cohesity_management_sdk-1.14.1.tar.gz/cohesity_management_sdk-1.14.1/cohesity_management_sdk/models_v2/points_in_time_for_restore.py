# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.time_range

class PointsInTimeForRestore(object):

    """Implementation of the 'Points in time for restore' model.

    Specifies the points in time available for restore as a set of one or more
    time ranges. If the number of available ranges exceeds 1000, then the
    latest 1000 will be returned.

    Attributes:
        time_ranges (list of TimeRange): Specifies the time ranges within
            which this object can be restored to any point in time. If the
            number of available ranges exceeds 1000, then the latest 1000 will
            be returned.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "time_ranges":'timeRanges'
    }

    def __init__(self,
                 time_ranges=None):
        """Constructor for the PointsInTimeForRestore class"""

        # Initialize members of the class
        self.time_ranges = time_ranges


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
        time_ranges = None
        if dictionary.get("timeRanges") is not None:
            time_ranges = list()
            for structure in dictionary.get('timeRanges'):
                time_ranges.append(cohesity_management_sdk.models_v2.time_range.TimeRange.from_dictionary(structure))

        # Return an object of this model
        return cls(time_ranges)


