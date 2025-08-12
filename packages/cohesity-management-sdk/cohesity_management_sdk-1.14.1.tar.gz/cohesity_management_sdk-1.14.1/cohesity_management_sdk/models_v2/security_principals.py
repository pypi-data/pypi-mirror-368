# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.security_principal

class SecurityPrincipals(object):

    """Implementation of the 'SecurityPrincipals' model.

    Specifies a list of security principals.

    Attributes:
        security_principals (list of SecurityPrincipal): Specifies a list of
            security principals.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "security_principals":'securityPrincipals'
    }

    def __init__(self,
                 security_principals=None):
        """Constructor for the SecurityPrincipals class"""

        # Initialize members of the class
        self.security_principals = security_principals


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
        security_principals = None
        if dictionary.get("securityPrincipals") is not None:
            security_principals = list()
            for structure in dictionary.get('securityPrincipals'):
                security_principals.append(cohesity_management_sdk.models_v2.security_principal.SecurityPrincipal.from_dictionary(structure))

        # Return an object of this model
        return cls(security_principals)


