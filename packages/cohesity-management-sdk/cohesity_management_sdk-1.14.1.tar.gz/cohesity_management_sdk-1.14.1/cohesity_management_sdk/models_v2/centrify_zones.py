# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.centrify_zone

class CentrifyZones(object):

    """Implementation of the 'CentrifyZones' model.

    Specifies a list of centrify zones for a domain.

    Attributes:
        domain_name (string): Specifies a domain name with these centrify
            zones.
        centrify_zones (list of CentrifyZone): Specifies a list of centrify
            zones for this domain.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "domain_name":'domainName',
        "centrify_zones":'centrifyZones'
    }

    def __init__(self,
                 domain_name=None,
                 centrify_zones=None):
        """Constructor for the CentrifyZones class"""

        # Initialize members of the class
        self.domain_name = domain_name
        self.centrify_zones = centrify_zones


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
        centrify_zones = None
        if dictionary.get("centrifyZones") is not None:
            centrify_zones = list()
            for structure in dictionary.get('centrifyZones'):
                centrify_zones.append(cohesity_management_sdk.models_v2.centrify_zone.CentrifyZone.from_dictionary(structure))

        # Return an object of this model
        return cls(domain_name,
                   centrify_zones)


