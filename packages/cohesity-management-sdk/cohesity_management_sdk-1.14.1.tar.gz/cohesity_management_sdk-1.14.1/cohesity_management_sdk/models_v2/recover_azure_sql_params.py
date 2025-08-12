# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_azure_sql_snapshot_params
import cohesity_management_sdk.models_v2.azure_target_params_for_recover_azure_sql

class RecoverAzureSqlParams(object):

    """Implementation of the 'Recover Azure Sql Params.' model.

    Specifies the parameters to recover Azure files and folders.

    Attributes:
        snapshots (list of RecoverAzureSqlSnapshotParams): Specifies the
            info about the files and folders to be recovered.
        target_environment (string): Specifies the environment of the recovery
            target. The corresponding params below must be filled out.
        azure_target_params (AzureTargetParamsForRecoverAzureSql): Specifies the params for
            recovering to an Azure target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "snapshots":'snapshots',
        "target_environment":'targetEnvironment',
        "azure_target_params":'azureTargetParams'
    }

    def __init__(self,
                 snapshots=None,
                 target_environment='kAzure',
                 azure_target_params=None):
        """Constructor for the RecoverAzureSqlParams class"""

        # Initialize members of the class
        self.snapshots = snapshots
        self.target_environment = target_environment
        self.azure_target_params = azure_target_params


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
        snapshots = None
        if dictionary.get("snapshots") is not None:
            snapshots = list()
            for structure in dictionary.get('snapshots'):
                snapshots.append(cohesity_management_sdk.models_v2.recover_azure_sql_snapshot_params.RecoverAzureSqlSnapshotParams.from_dictionary(structure))
        target_environment = dictionary.get("targetEnvironment") if dictionary.get("targetEnvironment") else 'kAzure'
        azure_target_params = cohesity_management_sdk.models_v2.azure_target_params_for_recover_azure_sql.AzureTargetParamsForRecoverAzureSql.from_dictionary(dictionary.get('azureTargetParams')) if dictionary.get('azureTargetParams') else None

        # Return an object of this model
        return cls(snapshots,
                   target_environment,
                   azure_target_params)