# -*- coding: utf-8 -*-


class TimeRange(object):

    """Implementation of the 'Time range.' model.

    Specifies a valid time range to which this object can be recovered.

    Attributes:
        start_time_usecs (long|int): Specifies the start time of this time
            range.
        end_time_usecs (long|int): Specifies the end time of this time range.
        protection_group_id (string): Specifies id of the Protection Group
            corresponding to this time range.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "protection_group_id":'protectionGroupId'
    }

    def __init__(self,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 protection_group_id=None):
        """Constructor for the TimeRange class"""

        # Initialize members of the class
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.protection_group_id = protection_group_id


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
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')
        protection_group_id = dictionary.get('protectionGroupId')

        # Return an object of this model
        return cls(start_time_usecs,
                   end_time_usecs,
                   protection_group_id)


