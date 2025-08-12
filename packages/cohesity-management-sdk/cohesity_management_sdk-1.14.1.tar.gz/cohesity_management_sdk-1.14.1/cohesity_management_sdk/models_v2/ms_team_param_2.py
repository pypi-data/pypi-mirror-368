# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.channel_param
class MsTeamParam2(object):

    """Implementation of the 'MsTeamParam2' model.

    Specifies parameters to recover a Microsoft 365 Team.

    Attributes:
        channel_params (list of ChannelParam): Specifies the list of Channels to recover. These are applicable
          iff recoverEntireMsTeam is false.
        recover_entire_ms_team (bool): Specifies whether to recover the whole
            Microsoft 365 Team.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "channel_params":'channelParams',
        "recover_entire_ms_team":'recoverEntireMsTeam'
    }

    def __init__(self,
                 channel_params=None,
                 recover_entire_ms_team=None):
        """Constructor for the MsTeamParam2 class"""

        # Initialize members of the class
        self.channel_params = channel_params
        self.recover_entire_ms_team = recover_entire_ms_team


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
        channel_params = None,
        if dictionary.get('channelParams') is not None:
            channel_params = list()
            for structure in dictionary.get('channelParams'):
                channel_params.append(cohesity_management_sdk.models_v2.channel_param.ChannelParam.from_dictionary(structure))
        recover_entire_ms_team = dictionary.get('recoverEntireMsTeam')

        # Return an object of this model
        return cls(
            channel_params,
            recover_entire_ms_team)