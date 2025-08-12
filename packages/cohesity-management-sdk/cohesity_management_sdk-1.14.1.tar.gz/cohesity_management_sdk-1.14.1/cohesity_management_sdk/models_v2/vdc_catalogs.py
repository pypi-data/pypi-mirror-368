# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vdc_catalog

class VDCCatalogs(object):

    """Implementation of the 'VDC Catalogs' model.

    Specifies a list of VDC Catalogs.

    Attributes:
        catalogs (list of VDCCatalog): Specifies a list of VDC Catalogs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "catalogs":'catalogs'
    }

    def __init__(self,
                 catalogs=None):
        """Constructor for the VDCCatalogs class"""

        # Initialize members of the class
        self.catalogs = catalogs


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
        catalogs = None
        if dictionary.get("catalogs") is not None:
            catalogs = list()
            for structure in dictionary.get('catalogs'):
                catalogs.append(cohesity_management_sdk.models_v2.vdc_catalog.VDCCatalog.from_dictionary(structure))

        # Return an object of this model
        return cls(catalogs)


