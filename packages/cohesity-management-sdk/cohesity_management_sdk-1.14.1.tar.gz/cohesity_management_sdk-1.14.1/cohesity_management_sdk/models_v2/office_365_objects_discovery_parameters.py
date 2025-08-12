# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.office_365_preservation_hold_library_params
import cohesity_management_sdk.models_v2.source_discovery_parameter_for_k_user_objecttype
import cohesity_management_sdk.models_v2.source_additional_parameter_for_teamsobject_type
import cohesity_management_sdk.models_v2.source_additional_parameter_for_share_point_site_object_type


class Office365ObjectsDiscoveryparameters(object):

    """Implementation of the 'Office365 Objects Discovery parameters.' model.

    Specifies the parameters used for discovering the office 365 objects
      selectively during source registration or refresh.

    Attributes:
        discoverable_object_type_list (list of DiscoverableObjectTypeListEnum): Specifies the list of object types that will be discovered as
          part of source registration or refresh.
        sites_discovery_params (Office365PreservationHoldLibraryParams):
          Specifies the parameters specific to the protection of the Preservation
          Hold library.
        teams_additional_params (): Specifies additional params for Teams entities.
        users_discovery_params (SourceDiscoveryParameterforkUserObjecttype): Specifies the discovery params for User(mailbox/onedrive) entities.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "discoverable_object_type_list":'discoverableObjectTypeList',
        "sites_discovery_params":'sitesDiscoveryParams',
        "teams_additional_params":'teamsAdditionalParams',
        "users_discovery_params":'usersDiscoveryParams'

    }

    def __init__(self,
                 discoverable_object_type_list=None,
                 sites_discovery_params=None,
                 teams_additional_params=None,
                 users_discovery_params=None
                 ):
        """Constructor for the Office365 Objects Discovery parameters class"""

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
        discoverable_object_type_list = dictionary.get('discoverableObjectTypeList')
        sites_discovery_params = cohesity_management_sdk.models_v2.source_additional_parameter_for_share_point_site_object_type.SourceAdditionalParameterForSharePointSiteObjectType.from_dictionary(
             dictionary.get('sitesDiscoveryParams')) if dictionary.get('sitesDiscoveryParams') else None
        teams_additional_params = cohesity_management_sdk.models_v2.source_additional_parameter_for_teamsobject_type.SourceAdditionalParameterForTeamsobjectType.from_dictionary(
            dictionary.get('teamsAdditionalParams')) if dictionary.get('teamsAdditionalParams') else None
        users_discovery_params = cohesity_management_sdk.models_v2.source_discovery_parameter_for_k_user_objecttype.SourceDiscoveryParameterforkUserObjecttype.from_dictionary(
            dictionary.get('usersDiscoveryParams')) if dictionary.get('usersDiscoveryParams') else None

        # Return an object of this model
        return cls(discoverable_object_type_list,
                   sites_discovery_params,
                   teams_additional_params,
                   users_discovery_params)