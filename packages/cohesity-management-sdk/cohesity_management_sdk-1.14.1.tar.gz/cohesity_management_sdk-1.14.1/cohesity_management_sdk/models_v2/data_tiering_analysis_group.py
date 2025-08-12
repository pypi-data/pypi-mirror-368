# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.data_tiering_source
import cohesity_management_sdk.models_v2.data_tiering_analysis_group_run

class DataTieringAnalysisGroup(object):

    """Implementation of the 'DataTieringAnalysisGroup' model.

    Specifies the data tiering analysis group.

    Attributes:
        name (string): Specifies the name of the data tiering analysis group.
        source (DataTieringSource): Specifies the source data tiering
            details.
        id (string): Specifies the ID of the data tiering analysis group.
        last_run (DataTieringAnalysisGroupRun): Specifies the data tiering
            analysis group run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "source":'source',
        "id":'id',
        "last_run":'lastRun'
    }

    def __init__(self,
                 name=None,
                 source=None,
                 id=None,
                 last_run=None):
        """Constructor for the DataTieringAnalysisGroup class"""

        # Initialize members of the class
        self.name = name
        self.source = source
        self.id = id
        self.last_run = last_run


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
        name = dictionary.get('name')
        source = cohesity_management_sdk.models_v2.data_tiering_source.DataTieringSource.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None
        id = dictionary.get('id')
        last_run = cohesity_management_sdk.models_v2.data_tiering_analysis_group_run.DataTieringAnalysisGroupRun.from_dictionary(dictionary.get('lastRun')) if dictionary.get('lastRun') else None

        # Return an object of this model
        return cls(name,
                   source,
                   id,
                   last_run)


