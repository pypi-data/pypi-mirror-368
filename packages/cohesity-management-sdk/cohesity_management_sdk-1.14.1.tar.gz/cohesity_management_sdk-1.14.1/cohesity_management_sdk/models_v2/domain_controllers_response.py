# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.domain_controllers

class DomainControllersResponse(object):

    """Implementation of the 'DomainControllersResponse' model.

    Specifies the response of get domain controllers request.

    Attributes:
        domain_controllers (list of DomainControllers): A list of domain names
            with a list of it's domain controllers.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "domain_controllers":'domainControllers'
    }

    def __init__(self,
                 domain_controllers=None):
        """Constructor for the DomainControllersResponse class"""

        # Initialize members of the class
        self.domain_controllers = domain_controllers


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
        domain_controllers = None
        if dictionary.get("domainControllers") is not None:
            domain_controllers = list()
            for structure in dictionary.get('domainControllers'):
                domain_controllers.append(cohesity_management_sdk.models_v2.domain_controllers.DomainControllers.from_dictionary(structure))

        # Return an object of this model
        return cls(domain_controllers)


