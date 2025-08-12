# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_ms_team_param
import cohesity_management_sdk.models_v2.target_ms_team_param

class RecoverMsTeamParams(object):

    """Implementation of the 'RecoverMsTeamParams' model.

    Specifies the parameters to recover Microsoft 365 Teams.

    Attributes:
        objects (list of ObjectMsTeamParam): Specifies a list of Microsoft 365
            Teams params associated with objects to recover.
        target_ms_team (TargetMsTeamParam): Specifies the target Team to
            recover to. If not specified, the objects will be recovered to
            original location.
        continue_on_error (bool): Specifies whether to continue recovering
            other teams, if some of the teams fail to recover. Default value
            is false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "target_ms_team":'targetMsTeam',
        "continue_on_error":'continueOnError'
    }

    def __init__(self,
                 objects=None,
                 target_ms_team=None,
                 continue_on_error=None):
        """Constructor for the RecoverMsTeamParams class"""

        # Initialize members of the class
        self.objects = objects
        self.target_ms_team = target_ms_team
        self.continue_on_error = continue_on_error


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
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.object_ms_team_param.ObjectMsTeamParam.from_dictionary(structure))
        target_ms_team = cohesity_management_sdk.models_v2.target_ms_team_param.TargetMsTeamParam.from_dictionary(dictionary.get('targetMsTeam')) if dictionary.get('targetMsTeam') else None
        continue_on_error = dictionary.get('continueOnError')

        # Return an object of this model
        return cls(objects,
                   target_ms_team,
                   continue_on_error)


