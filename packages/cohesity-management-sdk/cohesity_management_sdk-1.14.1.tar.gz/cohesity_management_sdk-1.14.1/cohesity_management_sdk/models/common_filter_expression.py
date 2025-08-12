# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.common_filter_expression_filter_policy

class CommonFilterExpression(object):

    """Implementation of the 'CommonFilterExpression' model.

    Message containing common params for filtering. This message is in the form
      of expression and complex expressions can be supported by adding more
      operations.
      Each expression contains exactly one of the fields - either a filter_policy
      which is a leaf node in the expression tree or one of the expression fields
      which will be intermediate nodes in the expression tree.
      The actual filter policies will only be specified at the leaf level of the
      expression.

    Attributes:
        filter_policy (CommonFilterExpression_FilterPolicy): The individual filter policy that specifies the filters to be applied.
          This is the leaf node of the expression tree.

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
        filter_policy = cohesity_management_sdk.models.common_filter_expression_filter_policy.CommonFilterExpression_FilterPolicy.from_dictionary(dictionary.get('filterPolicy')) if dictionary.get('filterPolicy') else None

        # Return an object of this model
        return cls(filter_policy)