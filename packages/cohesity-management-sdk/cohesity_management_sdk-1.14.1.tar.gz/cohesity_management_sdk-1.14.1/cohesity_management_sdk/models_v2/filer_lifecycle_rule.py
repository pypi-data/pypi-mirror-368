# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.filer_lifecycle_aging_policy
import cohesity_management_sdk.models_v2.filer_lifecycle_rule_filter


class FilerLifecycleRule(object):

    """Implementation of the 'FilerLifecycleRule' model.

    Specifies the Lifecycle configuration rule.

    Attributes:
        aging_policy (FilerLifecycleAgingPolicy): Specifies the file''s selection based on of the following: last
          modification time, creation time or last access time. This filed is mandatory
          for rules that are Allow type. Note: Both the fields days and dateInUsecs
          are mutually exclusive to each other.
        file_filter (FilerLifecycleRuleFilter): Specifies the filter used to identify files that a Lifecycle
          Rule applies to.
        name (string): Specifies the Unique identifier for the rule. No 2 rules in a
          policy should have the same name. The value cannot be longer than 255 characters.
        status (Status33Enum): Specifies if the rule is currently being applied.
        mtype (TypeEnum): Specifies if the rule is Allow or Deny type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "aging_policy":'agingPolicy',
        "file_filter":'fileFilter',
        "name":'name',
        "status":'status',
        "mtype":"type"
    }

    def __init__(self,
                 aging_policy=None,
                 file_filter=None,
                 name=None,
                 status=None,
                 mtype=None):
        """Constructor for the FilerLifecycleRule class"""

        # Initialize members of the class
        self.aging_policy = aging_policy
        self.file_filter = file_filter
        self.name = name
        self.status = status
        self.mtype = mtype


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
        aging_policy = cohesity_management_sdk.models_v2.filer_lifecycle_aging_policy.FilerLifecycleAgingPolicy.from_dictionary(dictionary.get('agingPolicy')) if dictionary.get('agingPolicy') else None
        file_filter = cohesity_management_sdk.models_v2.filer_lifecycle_rule_filter.FilerLifecycleRuleFilter.from_dictionary(dictionary.get('fileFilter')) if dictionary.get('fileFilter') else None
        name = dictionary.get('name')
        status = dictionary.get('status')
        mtype = dictionary.get('type')

        # Return an object of this model
        return cls(aging_policy,
                   file_filter,
                   name,
                   status,
                   mtype)