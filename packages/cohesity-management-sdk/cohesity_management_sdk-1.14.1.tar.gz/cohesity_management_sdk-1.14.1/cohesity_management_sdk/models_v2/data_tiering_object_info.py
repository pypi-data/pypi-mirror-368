# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.data_tiering_object_analysis_info

class DataTieringObjectInfo(object):

    """Implementation of the 'DataTieringObjectInfo' model.

    Specifies the data tiering analysis group run object details.

    Attributes:
        id (long|int): Specifies the ID of the object.
        name (string): Specifies the name of the object.
        analysis_info (DataTieringObjectAnalysisInfo): Specifies the data
            tiering object analysis details.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "analysis_info":'analysisInfo'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 analysis_info=None):
        """Constructor for the DataTieringObjectInfo class"""

        # Initialize members of the class
        self.id = id
        self.name = name
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
        name = dictionary.get('name')
        analysis_info = cohesity_management_sdk.models_v2.data_tiering_object_analysis_info.DataTieringObjectAnalysisInfo.from_dictionary(dictionary.get('analysisInfo')) if dictionary.get('analysisInfo') else None

        # Return an object of this model
        return cls(id,
                   name,
                   analysis_info)


