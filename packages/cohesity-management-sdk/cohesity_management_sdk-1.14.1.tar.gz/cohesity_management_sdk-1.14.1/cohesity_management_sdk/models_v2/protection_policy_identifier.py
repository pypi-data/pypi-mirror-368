# -*- coding: utf-8 -*-


class ProtectionPolicyIdentifier(object):

    """Implementation of the 'Protection Policy Identifier.' model.

    Specifies Protection Policy Identifier.

    Attributes:
        protection_policy_id (string): Specifies Protection Policy id.
        protection_policy_name (string): Specifies Protection Policy name.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_policy_id":'protectionPolicyId',
        "protection_policy_name":'protectionPolicyName'
    }

    def __init__(self,
                 protection_policy_id=None,
                 protection_policy_name=None):
        """Constructor for the ProtectionPolicyIdentifier class"""

        # Initialize members of the class
        self.protection_policy_id = protection_policy_id
        self.protection_policy_name = protection_policy_name


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
        protection_policy_id = dictionary.get('protectionPolicyId')
        protection_policy_name = dictionary.get('protectionPolicyName')

        # Return an object of this model
        return cls(protection_policy_id,
                   protection_policy_name)


