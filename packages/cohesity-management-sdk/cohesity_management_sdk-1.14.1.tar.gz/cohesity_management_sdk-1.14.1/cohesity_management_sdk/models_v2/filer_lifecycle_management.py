# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.filer_lifecycle_rule

class FilerLifecycleManagement(object):

    """Implementation of the 'FilerLifecycleManagement' model.

   Specifies the filer Lifecycle policy of a NFS/SMB view. If not specified
      no Lifecycle management is performed for entites in filer view.

    Attributes:
        rules (list of FilerLifecycleRule): Specifies Lifecycle configuration
          rules for a filer view. A maximum of 100 rules can be specified.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "rules":'rules'
    }

    def __init__(self,
                 rules=None):
        """Constructor for the FilerLifecycleManagement class"""

        # Initialize members of the class
        self.rules = rules


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
                rules.append(cohesity_management_sdk.models_v2.filer_lifecycle_rule.FilerLifecycleRule.from_dictionary(structure))


        # Return an object of this model
        return cls(rules)