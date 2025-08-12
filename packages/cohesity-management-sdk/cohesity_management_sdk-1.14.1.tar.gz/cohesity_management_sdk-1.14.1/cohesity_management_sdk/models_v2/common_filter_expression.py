# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models_v2.common_filter_policy

class CommonFilterExpression(object):

    """Implementation of the 'CommonFilterExpression' model.

    Specifies the params for filtering an entity. Exactly one of the
      child objects should be specified for this object.

    Attributes:
        filter_policy (CommonFilterPolicy): Specifies the filter policy for an entity.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "filter_policy": 'filterPolicy'
    }

    def __init__(self,
                 filter_policy=None):
        """Constructor for the CommonFilterExpression class"""

        # Initialize members of the class
        self.filter_policy = filter_policy


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
        filter_policy = cohesity_management_sdk.models_v2.common_filter_policy.CommonFilterPolicy.from_dictionary(dictionary.get('filterPolicy')) if dictionary.get('filterPolicy') else None

        # Return an object of this model
        return cls(filter_policy)