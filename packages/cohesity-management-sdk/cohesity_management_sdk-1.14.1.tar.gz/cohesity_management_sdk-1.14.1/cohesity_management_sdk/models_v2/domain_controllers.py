# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.domain_controller

class DomainControllers(object):

    """Implementation of the 'DomainControllers' model.

    Specifies the domain controllers of a domain.

    Attributes:
        domain_name (string): Specifies the domain name.
        controllers (list of DomainController): Specifies a list of domain
            controllers of the domain.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "domain_name":'domainName',
        "controllers":'controllers'
    }

    def __init__(self,
                 domain_name=None,
                 controllers=None):
        """Constructor for the DomainControllers class"""

        # Initialize members of the class
        self.domain_name = domain_name
        self.controllers = controllers


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
        controllers = None
        if dictionary.get("controllers") is not None:
            controllers = list()
            for structure in dictionary.get('controllers'):
                controllers.append(cohesity_management_sdk.models_v2.domain_controller.DomainController.from_dictionary(structure))

        # Return an object of this model
        return cls(domain_name,
                   controllers)


