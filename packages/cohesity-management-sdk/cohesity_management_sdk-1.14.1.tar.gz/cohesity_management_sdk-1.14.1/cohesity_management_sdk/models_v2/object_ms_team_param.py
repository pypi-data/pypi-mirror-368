# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.ms_team_param_2
import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params

class ObjectMsTeamParam(object):

    """Implementation of the 'ObjectMsTeamParam' model.

    Specifies recovery parameters associated with a Microsoft 365 Team.

    Attributes:
        recover_object (CommonRecoverObjectSnapshotParams): Specifies the Microsoft 365 Team
            recover object info.
        ms_team_param (MsTeamParam2): Specifies parameters to recover a
            Microsoft 365 Team.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recover_object":'recoverObject',
        "ms_team_param":'msTeamParam'
    }

    def __init__(self,
                 recover_object=None,
                 ms_team_param=None):
        """Constructor for the ObjectMsTeamParam class"""

        # Initialize members of the class
        self.recover_object = recover_object
        self.ms_team_param = ms_team_param


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
        recover_object = cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(dictionary.get('recoverObject')) if dictionary.get('recoverObject') else None
        ms_team_param = cohesity_management_sdk.models_v2.ms_team_param_2.MsTeamParam2.from_dictionary(dictionary.get('msTeamParam')) if dictionary.get('msTeamParam') else None

        # Return an object of this model
        return cls(recover_object,
                   ms_team_param)