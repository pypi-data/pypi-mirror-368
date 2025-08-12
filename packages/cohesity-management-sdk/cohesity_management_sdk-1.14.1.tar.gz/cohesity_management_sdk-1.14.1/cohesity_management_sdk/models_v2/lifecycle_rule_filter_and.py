# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.lifecycle_rule_filter_tag

class LifecycleRuleFilterAnd(object):

    """Implementation of the 'LifecycleRuleFilterAnd' model.

    Specifies the Lifecycle configuration Rule Filter AND element.

    Attributes:
        prefix (string): Specifies a Prefix identifying one or more objects to which the
          rule applies.
        tags (list of LifecycleRuleFilterTag): Specifies the tag in the object's tag set to which the rule applies.
          All of these tags must exist in the object's tag set in order for the rule
          to apply.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "prefix":'prefix',
        "tags":'tags'
    }

    def __init__(self,
                 prefix=None,
                 tags=None):
        """Constructor for the LifecycleRuleFilterAnd class"""

        # Initialize members of the class
        self.prefix = prefix
        self.tags = tags


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
        prefix = dictionary.get('prefix')
        tags = None
        if dictionary.get('tags') is not None:
            tags = list()
            for structure in dictionary.get('tags'):
                tags.append(cohesity_management_sdk.models_v2.lifecycle_rule_filter_tag.LifecycleRuleFilterTag.from_dictionary(structure))

        # Return an object of this model
        return cls(prefix,
                   tags)