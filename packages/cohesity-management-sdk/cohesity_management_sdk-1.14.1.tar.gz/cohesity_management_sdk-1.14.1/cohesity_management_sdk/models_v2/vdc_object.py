# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vdc_catalog
import cohesity_management_sdk.models_v2.org_vdc_network

class VdcObject(object):

    """Implementation of the 'VdcObject' model.

    Specifies the details about VMware Virtual datacenter.

    Attributes:
        catalogs (list of VDCCatalog): Specifies a list of VDC Catalogs.
        org_networks (list of OrgVDCNetwork): Specifies a list of Organization
            VDC Networks.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "catalogs":'catalogs',
        "org_networks":'orgNetworks'
    }

    def __init__(self,
                 catalogs=None,
                 org_networks=None):
        """Constructor for the VdcObject class"""

        # Initialize members of the class
        self.catalogs = catalogs
        self.org_networks = org_networks


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
        org_networks = None
        if dictionary.get("orgNetworks") is not None:
            org_networks = list()
            for structure in dictionary.get('orgNetworks'):
                org_networks.append(cohesity_management_sdk.models_v2.org_vdc_network.OrgVDCNetwork.from_dictionary(structure))

        # Return an object of this model
        return cls(catalogs,
                   org_networks)


