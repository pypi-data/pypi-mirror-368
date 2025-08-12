# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.up_tiering_inclusion_policy
import cohesity_management_sdk.models_v2.up_tiering_exclusion_policy

class UpTieringPolicy(object):

    """Implementation of the 'UpTieringPolicy' model.

    Specifies the Data Migration uptiering policy.

    Attributes:
        inclusion (UpTieringInclusionPolicy): Specifies the files selection
            rules for uptiering.
        exclusion (UpTieringExclusionPolicy): Specifies the files exclusion
            rules for uptiering.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "inclusion":'inclusion',
        "exclusion":'exclusion'
    }

    def __init__(self,
                 inclusion=None,
                 exclusion=None):
        """Constructor for the UpTieringPolicy class"""

        # Initialize members of the class
        self.inclusion = inclusion
        self.exclusion = exclusion


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
        inclusion = cohesity_management_sdk.models_v2.up_tiering_inclusion_policy.UpTieringInclusionPolicy.from_dictionary(dictionary.get('inclusion')) if dictionary.get('inclusion') else None
        exclusion = cohesity_management_sdk.models_v2.up_tiering_exclusion_policy.UpTieringExclusionPolicy.from_dictionary(dictionary.get('exclusion')) if dictionary.get('exclusion') else None

        # Return an object of this model
        return cls(inclusion,
                   exclusion)


