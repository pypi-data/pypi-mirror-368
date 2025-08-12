# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class SitesDiscoveryParams(object):

    """Implementation of the 'SitesDiscoveryParams' model.

    Specifies discovery params for kSite entities. It should only be populated
    when the 'DiscoveryParams.discoverableObjectTypeList' includes 'kSites'.

    Attributes:
        enable_site_tagging (bool): Specifies whether the SharePoint Sites will
            be tagged whether they belong to a group site or teams site.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enable_site_tagging":'enableSiteTagging'
    }

    def __init__(self,
                 enable_site_tagging=None):
        """Constructor for the SitesDiscoveryParams class"""

        # Initialize members of the class
        self.enable_site_tagging = enable_site_tagging


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
        enable_site_tagging = dictionary.get('enableSiteTagging')

        # Return an object of this model
        return cls(enable_site_tagging)


