# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.tiering_info

class DataTieringTaskRun(object):

    """Implementation of the 'DataTieringTaskRun' model.

    Specifies the data tiering task run.

    Attributes:
        id (string): Specifies the id of the data tiering task run.
        start_time_usecs (long|int): Specifies the start time of task run in
            Unix epoch Timestamp(in microseconds).
        end_time_usecs (long|int): Specifies the end time of task run in Unix
            epoch Timestamp(in microseconds).
        tiering_info (TieringInfo): Specifies the data tiering task details.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "tiering_info":'tieringInfo'
    }

    def __init__(self,
                 id=None,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 tiering_info=None):
        """Constructor for the DataTieringTaskRun class"""

        # Initialize members of the class
        self.id = id
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.tiering_info = tiering_info


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
        id = dictionary.get('id')
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')
        tiering_info = cohesity_management_sdk.models_v2.tiering_info.TieringInfo.from_dictionary(dictionary.get('tieringInfo')) if dictionary.get('tieringInfo') else None

        # Return an object of this model
        return cls(id,
                   start_time_usecs,
                   end_time_usecs,
                   tiering_info)


