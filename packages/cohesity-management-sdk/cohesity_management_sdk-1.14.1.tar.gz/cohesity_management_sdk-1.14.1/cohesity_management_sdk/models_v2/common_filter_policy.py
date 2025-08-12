# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models_v2.o_365_restore_exclusion_policy

class CommonFilterPolicy(object):

    """Implementation of the 'CommonFilterPolicy' model.

    Specifies the filter policy for filtering an entity.

    Attributes:
        office_365_restore_exclusion_policy (O365RestoreExclusionPolicy):
             Specifies the filter policy to be applied for exclusions in
            Microsoft 365 restores.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "office_365_restore_exclusion_policy": 'office365RestoreExclusionPolicy'
    }

    def __init__(self,
                 office_365_restore_exclusion_policy=None):
        """Constructor for the CommonFilterPolicy class"""

        # Initialize members of the class
        self.office_365_restore_exclusion_policy = office_365_restore_exclusion_policy


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
        office_365_restore_exclusion_policy = cohesity_management_sdk.models_v2.o_365_restore_exclusion_policy.O365RestoreExclusionPolicy.from_dictionary(dictionary.get('office365RestoreExclusionPolicy')) if dictionary.get('office365RestoreExclusionPolicy') else None

        # Return an object of this model
        return cls(office_365_restore_exclusion_policy)