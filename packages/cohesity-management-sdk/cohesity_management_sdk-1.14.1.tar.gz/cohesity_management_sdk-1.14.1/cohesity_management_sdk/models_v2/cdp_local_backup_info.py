# -*- coding: utf-8 -*-


class CdpLocalBackupInfo(object):

    """Implementation of the 'CdpLocalBackupInfo' model.

    Specifies the last local backup information for a given CDP object.

    Attributes:
        start_time_in_usecs (long|int): Specifies the start time of the last
            local backup taken.
        end_time_in_usecs (long|int): Specifies the end time of the last local
            backup taken.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "start_time_in_usecs":'startTimeInUsecs',
        "end_time_in_usecs":'endTimeInUsecs'
    }

    def __init__(self,
                 start_time_in_usecs=None,
                 end_time_in_usecs=None):
        """Constructor for the CdpLocalBackupInfo class"""

        # Initialize members of the class
        self.start_time_in_usecs = start_time_in_usecs
        self.end_time_in_usecs = end_time_in_usecs


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
        start_time_in_usecs = dictionary.get('startTimeInUsecs')
        end_time_in_usecs = dictionary.get('endTimeInUsecs')

        # Return an object of this model
        return cls(start_time_in_usecs,
                   end_time_in_usecs)


