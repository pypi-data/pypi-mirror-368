# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.lifecycle_rule

class S3LifecycleManagement(object):

    """Implementation of the 'S3LifecycleManagement' model.

    Specifies the S3 Lifecycle policy of the bucket. If not specified
      no Lifecycle management is performed for objects in this bucket.

    Attributes:
        rules (list of LifecycleRule): Specifies Lifecycle configuration rules for an Amazon S3 bucket.
          A maximum of 1000 rules can be specified.
        version_id (long|int64): Specifies a unique monotonically increasing version for the lifecycle
          configuration.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "rules":'rules',
        "version_id":'versionId'
    }

    def __init__(self,
                 rules=None,
                 version_id=None):
        """Constructor for the S3LifecycleManagement class"""

        # Initialize members of the class
        self.rules = rules
        self.version_id = version_id


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
        rules = None
        if dictionary.get('rules') is not None:
            rules = list()
            for structure in dictionary.get('rules'):
                rules.append(cohesity_management_sdk.models_v2.lifecycle_rule.LifecycleRule.from_dictionary(structure))
        version_id = dictionary.get('versionId')

        # Return an object of this model
        return cls(rules,
                   version_id)