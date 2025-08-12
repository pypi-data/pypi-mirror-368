# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recovery_object_identifier
import cohesity_management_sdk.models_v2.target_teams_channel_param

class TargetMsTeamParam(object):

    """Implementation of the 'TargetMsTeamParam' model.

    Specifies the target Microsoft 365 Team to recover to.

    Attributes:
        parent_source_id (long|int): Specifies the id of the domain during alternate domain recovery.
        target_team (RecoveryObjectIdentifier): Specifies the selected existing target team info.
        target_teams_channel_param (TargetTeamsChannelParam): Specifies the ms team target channel parameters in case of granular
          restore to alternate location.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "parent_source_id":'parentSourceId',
        "target_team":'targetTeam',
        "target_teams_channel_param":'targetTeamsChannelParam'
    }

    def __init__(self,
                 parent_source_id=None,
                 target_team=None,
                 target_teams_channel_param=None):
        """Constructor for the TargetMsTeamParam class"""

        # Initialize members of the class
        self.parent_source_id = parent_source_id
        self.target_team = target_team
        self.target_teams_channel_param = target_teams_channel_param


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
        parent_source_id = dictionary.get('parentSourceId')
        target_team = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('targetTeam')) if dictionary.get('targetTeam') else None
        target_teams_channel_param = cohesity_management_sdk.models_v2.target_teams_channel_param.TargetTeamsChannelParam.from_dictionary(dictionary.get('targetTeamsChannelParam')) if dictionary.get('targetTeamsChannelParam') else None

        # Return an object of this model
        return cls(parent_source_id,
                    target_team,
                   target_teams_channel_param)