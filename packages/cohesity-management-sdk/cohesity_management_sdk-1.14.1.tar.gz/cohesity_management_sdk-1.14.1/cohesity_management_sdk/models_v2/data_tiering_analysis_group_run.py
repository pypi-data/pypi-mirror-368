# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.data_tiering_object_info
import cohesity_management_sdk.models_v2.data_tiering_analysis_info

class DataTieringAnalysisGroupRun(object):

    """Implementation of the 'DataTieringAnalysisGroupRun' model.

    Specifies the data tiering analysis group run.

    Attributes:
        id (string): Specifies the ID of the data tiering analysis group run.
        objects (list of DataTieringObjectInfo): Specifies the objects details
            analyzed during data tiering analysis group run.
        start_time_usecs (long|int): Specifies the start time of analysis run
            in Unix epoch Timestamp(in microseconds).
        end_time_usecs (long|int): Specifies the end time of analysis run in
            Unix epoch Timestamp(in microseconds).
        analysis_info (DataTieringAnalysisInfo): Specifies the data tiering
            analysis details.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "objects":'objects',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "analysis_info":'analysisInfo'
    }

    def __init__(self,
                 id=None,
                 objects=None,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 analysis_info=None):
        """Constructor for the DataTieringAnalysisGroupRun class"""

        # Initialize members of the class
        self.id = id
        self.objects = objects
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.analysis_info = analysis_info


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
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.data_tiering_object_info.DataTieringObjectInfo.from_dictionary(structure))
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')
        analysis_info = cohesity_management_sdk.models_v2.data_tiering_analysis_info.DataTieringAnalysisInfo.from_dictionary(dictionary.get('analysisInfo')) if dictionary.get('analysisInfo') else None

        # Return an object of this model
        return cls(id,
                   objects,
                   start_time_usecs,
                   end_time_usecs,
                   analysis_info)


