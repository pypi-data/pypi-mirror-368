# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.helios_policy_response

class HeliosPoliciesResponseWithPagination(object):

    """Implementation of the 'HeliosPoliciesResponseWithPagination' model.

    Specifies the list of Policies.

    Attributes:
        policies (list of HeliosPolicyResponse): Specifies a list of
            policies.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "policies":'policies'
    }

    def __init__(self,
                 policies=None):
        """Constructor for the HeliosPoliciesResponseWithPagination class"""

        # Initialize members of the class
        self.policies = policies


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
        policies = None
        if dictionary.get("policies") is not None:
            policies = list()
            for structure in dictionary.get('policies'):
                policies.append(cohesity_management_sdk.models_v2.helios_policy_response.HeliosPolicyResponse.from_dictionary(structure))

        # Return an object of this model
        return cls(policies)


