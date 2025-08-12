# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.domain_controller

class TrustedDomain(object):

    """Implementation of the 'TrustedDomain' model.

    Specifies the details of a trusted domain.

    Attributes:
        domain_name (string): Specifies a domain name.
        preferred_domain_controllers (list of DomainController): Specifies a
            list of preferred domain controllers for this domain.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "domain_name":'domainName',
        "preferred_domain_controllers":'preferredDomainControllers'
    }

    def __init__(self,
                 domain_name=None,
                 preferred_domain_controllers=None):
        """Constructor for the TrustedDomain class"""

        # Initialize members of the class
        self.domain_name = domain_name
        self.preferred_domain_controllers = preferred_domain_controllers


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
        domain_name = dictionary.get('domainName')
        preferred_domain_controllers = None
        if dictionary.get("preferredDomainControllers") is not None:
            preferred_domain_controllers = list()
            for structure in dictionary.get('preferredDomainControllers'):
                preferred_domain_controllers.append(cohesity_management_sdk.models_v2.domain_controller.DomainController.from_dictionary(structure))

        # Return an object of this model
        return cls(domain_name,
                   preferred_domain_controllers)


