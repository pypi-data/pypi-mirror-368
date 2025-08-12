# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_data_migration_source_analysis_group_params

class DataMigrationSourceAnalysisGroups(object):

    """Implementation of the 'DataMigrationSourceAnalysisGroups' model.

    Specifies the Data Migration source analysis groups.

    Attributes:
        data_migration_source_analysis_groups (list of
            DataMigrationSourceAnalysisGroup): Specifies the Data Migration
            source analysis groups.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "data_migration_source_analysis_groups":'DataMigrationSourceAnalysisGroups'
    }

    def __init__(self,
                 data_migration_source_analysis_groups=None):
        """Constructor for the DataMigrationSourceAnalysisGroups class"""

        # Initialize members of the class
        self.data_migration_source_analysis_groups = data_migration_source_analysis_groups


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
        data_migration_source_analysis_groups = None
        if dictionary.get("DataMigrationSourceAnalysisGroups") is not None:
            data_migration_source_analysis_groups = list()
            for structure in dictionary.get('DataMigrationSourceAnalysisGroups'):
                data_migration_source_analysis_groups.append(cohesity_management_sdk.models_v2.common_data_migration_source_analysis_group_params.DataMigrationSourceAnalysisGroup.from_dictionary(structure))

        # Return an object of this model
        return cls(data_migration_source_analysis_groups)


