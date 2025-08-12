# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.acl_grant

class AclConfig(object):

    """Implementation of the 'AclConfig' model.

    Specifies the ACL config of an S3 bucket.

    Attributes:
        grants (list of AclGrant): Specifies a list of ACL grants.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "grants":'grants'
    }

    def __init__(self,
                 grants=None):
        """Constructor for the AclConfig class"""

        # Initialize members of the class
        self.grants = grants


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
        grants = None
        if dictionary.get("grants") is not None:
            grants = list()
            for structure in dictionary.get('grants'):
                grants.append(cohesity_management_sdk.models_v2.acl_grant.AclGrant.from_dictionary(structure))

        # Return an object of this model
        return cls(grants)


