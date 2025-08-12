# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.users_discovery_params
import cohesity_management_sdk.models.sites_discovery_params
import cohesity_management_sdk.models.teams_additional_params


class ObjectsDiscoveryParams(object):

    """Implementation of the 'ObjectsDiscoveryParams' model.

    Specifies the parameters used for discovering the office 365 objects
    selectively during source registration or refresh.


    Attributes:

        discoverable_object_type_list (list of string): Specifies the list of
            object types that will be discovered as part of source registration
            or refresh.
        sites_discovery_params (SitesDiscoveryParams): Specifies the discovery
            params for SharePoint site entities.
        teams_additional_params (TeamsAdditionalParams): Specifies the
            additional params for Team entities.
        users_discovery_params (UsersDiscoveryParams): Specifies the discovery
            params for kUser entities.
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "discoverable_object_type_list":'discoverableObjectTypeList',
        "sites_discovery_params": 'sitesDiscoveryParams',
        "teams_additional_params": 'teamsAdditionalParams',
        "users_discovery_params":'usersDiscoveryParams',
    }
    def __init__(self,
                 discoverable_object_type_list=None,
                 sites_discovery_params=None,
                 teams_additional_params=None,
                 users_discovery_params=None,
            ):

        """Constructor for the ObjectsDiscoveryParams class"""

        # Initialize members of the class
        self.discoverable_object_type_list = discoverable_object_type_list
        self.sites_discovery_params = sites_discovery_params
        self.teams_additional_params = teams_additional_params
        self.users_discovery_params = users_discovery_params

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
        discoverable_object_type_list = dictionary.get("discoverableObjectTypeList")
        sites_discovery_params = cohesity_management_sdk.models.sites_discovery_params.SitesDiscoveryParams.from_dictionary(dictionary.get('sitesDiscoveryParams')) if dictionary.get('sitesDiscoveryParams') else None
        teams_additional_params = cohesity_management_sdk.models.teams_additional_params.TeamsAdditionalParams.from_dictionary(dictionary.get('teamsAdditionalParams')) if dictionary.get('teamsAdditionalParams') else None
        users_discovery_params = cohesity_management_sdk.models.users_discovery_params.UsersDiscoveryParams.from_dictionary(dictionary.get('usersDiscoveryParams')) if dictionary.get('usersDiscoveryParams') else None

        # Return an object of this model
        return cls(
            discoverable_object_type_list,
            sites_discovery_params,
            teams_additional_params,
            users_discovery_params
)