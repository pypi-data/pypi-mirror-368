# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.update_protection_group_run_request_params

class UpdateProtectionGroupRunRequestBody(object):

    """Implementation of the 'Update Protection Group Run Request Body.' model.

    Specifies the params to update a list of Protection Group Runs.

    Attributes:
        update_protection_group_run_params (list of
            UpdateProtectionGroupRunRequestParams): TODO: type description
            here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "update_protection_group_run_params":'updateProtectionGroupRunParams'
    }

    def __init__(self,
                 update_protection_group_run_params=None):
        """Constructor for the UpdateProtectionGroupRunRequestBody class"""

        # Initialize members of the class
        self.update_protection_group_run_params = update_protection_group_run_params


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
        update_protection_group_run_params = None
        if dictionary.get("updateProtectionGroupRunParams") is not None:
            update_protection_group_run_params = list()
            for structure in dictionary.get('updateProtectionGroupRunParams'):
                update_protection_group_run_params.append(cohesity_management_sdk.models_v2.update_protection_group_run_request_params.UpdateProtectionGroupRunRequestParams.from_dictionary(structure))

        # Return an object of this model
        return cls(update_protection_group_run_params)


