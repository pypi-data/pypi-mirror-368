# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.generic_nas_data_migration_params
import cohesity_management_sdk.models_v2.view_data_migration_parameters

class DataMigrationSource(object):

    """Implementation of the 'DataMigrationSource' model.

    Specifies the objects to be migrated.

    Attributes:
        environment (Environment3Enum): Specifies the environment type of the
            Data Migration.
        generic_nas_params (GenericNasDataMigrationParams): Specifies the
            parameters which are specific to NAS related Protection Groups.
        view_params (ViewDataMigrationParameters): Specifies the parameters
            which are specific to view related Data Migration endpoints.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "environment":'environment',
        "generic_nas_params":'genericNasParams',
        "view_params":'viewParams'
    }

    def __init__(self,
                 environment=None,
                 generic_nas_params=None,
                 view_params=None):
        """Constructor for the DataMigrationSource class"""

        # Initialize members of the class
        self.environment = environment
        self.generic_nas_params = generic_nas_params
        self.view_params = view_params


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
        environment = dictionary.get('environment')
        generic_nas_params = cohesity_management_sdk.models_v2.generic_nas_data_migration_params.GenericNasDataMigrationParams.from_dictionary(dictionary.get('genericNasParams')) if dictionary.get('genericNasParams') else None
        view_params = cohesity_management_sdk.models_v2.view_data_migration_parameters.ViewDataMigrationParameters.from_dictionary(dictionary.get('viewParams')) if dictionary.get('viewParams') else None

        # Return an object of this model
        return cls(environment,
                   generic_nas_params,
                   view_params)


