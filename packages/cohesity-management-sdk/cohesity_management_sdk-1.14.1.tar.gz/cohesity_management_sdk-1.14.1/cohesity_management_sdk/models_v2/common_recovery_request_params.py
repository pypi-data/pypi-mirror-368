# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_filter_expression

class CommonRecoveryRequestParams(object):

    """Implementation of the 'Common Recovery Request Params.' model.

    Specifies the common request parameters to create a Recovery.

    Attributes:
        filter_params (CommonFilterExpression): Specifies the params for filtering the entity to be recovered.
          Depending on the recovery type, this can be used to filter the items within
          an entity or the entities themselves.
        name (string): Specifies the name of the Recovery.
        snapshot_environment (SnapshotEnvironmentEnum): Specifies the type of
            environment of snapshots for which the Recovery has to be
            performed.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "filter_params":'filterParams',
        "name":'name',
        "snapshot_environment":'snapshotEnvironment'
    }

    def __init__(self,
                 filter_params=None,
                 name=None,
                 snapshot_environment=None):
        """Constructor for the CommonRecoveryRequestParams class"""

        # Initialize members of the class
        self.filter_params = filter_params
        self.name = name
        self.snapshot_environment = snapshot_environment


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
        filter_params = cohesity_management_sdk.models_v2.common_filter_expression.CommonFilterExpression.from_dictionary(dictionary.get('filterParams')) if dictionary.get('filterParams') else None
        name = dictionary.get('name')
        snapshot_environment = dictionary.get('snapshotEnvironment')

        # Return an object of this model
        return cls(filter_params,
                   name,
                   snapshot_environment)