# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models_v2.object_ms_team_param
import cohesity_management_sdk.models_v2.target_ms_team_param
import cohesity_management_sdk.models_v2.recovery_object_identifier

class RecoverMsTeamParams(object):
    """Implementation of the 'RecoverMsTeamParams' model.

    Specifies the parameters to recover Microsoft 365 Teams.

    Attributes:
        continue_on_error (bool): Specifies whether to continue recovering other teams, if some of the teams fail to recover. Default value is false.
        create_new_team (bool): Specifies to create new team in case the target team doesn't exists in case restoreToOriginal is false.
        objects (list of ObjectMsTeamParam): Specifies a list of Microsoft 365 Teams params associated with objects to recover.
        restore_original_owners (bool): Specifies if the original members/owners should be part of the newly created target team or not.
        restore_to_original (bool): Specifies whether or not all Microsoft 365 Teams are restored to original location.
        target_ms_team (TargetMsTeamParam): This field is deprecated. Use targetTeamNickName and targetTeamFullName instead.
        target_ms_team_param (TargetMsTeamParam): Specifies the ms team target parameters in case of restoreToOriginal is false.
        target_team_full_name (string): This field is deprecated. Specifies target team name in case restoreToOriginal is false. This will be ignored if restoring to alternate existing team (i.e. to a team the nickname of which is same as the one supplied by the end user).
        target_team_name (string): Specifies the target team name in case restoreToOriginal is false.
        target_team_nick_name (string): This field is deprecated. Specifies target team nickname in case restoreToOriginal is false.
        target_team_owner (RecoveryObjectIdentifier): Specifies the additional owner entity info for the selected target team.
    """

    _names = {
        "continue_on_error":"continueOnError",
        "create_new_team":"createNewTeam",
        "objects":"objects",
        "restore_original_owners":"restoreOriginalOwners",
        "restore_to_original":"restoreToOriginal",
        "target_ms_team":"targetMsTeam",
        "target_ms_team_param":"targetMsTeamParam",
        "target_team_full_name":"targetTeamFullName",
        "target_team_name":"targetTeamName",
        "target_team_nick_name":"targetTeamNickName",
        "target_team_owner":"targetTeamOwner",
    }

    def __init__(self,
                 continue_on_error=None,
                 create_new_team=None,
                 objects=None,
                 restore_original_owners=None,
                 restore_to_original=None,
                 target_ms_team=None,
                 target_ms_team_param=None,
                 target_team_full_name=None,
                 target_team_name=None,
                 target_team_nick_name=None,
                 target_team_owner=None):
        """Constructor for the RecoverMsTeamParams class"""

        self.continue_on_error = continue_on_error
        self.create_new_team = create_new_team
        self.objects = objects
        self.restore_original_owners = restore_original_owners
        self.restore_to_original = restore_to_original
        self.target_ms_team = target_ms_team
        self.target_ms_team_param = target_ms_team_param
        self.target_team_full_name = target_team_full_name
        self.target_team_name = target_team_name
        self.target_team_nick_name = target_team_nick_name
        self.target_team_owner = target_team_owner


    @classmethod
    def from_dictionary(cls, dictionary):
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

        continue_on_error = dictionary.get('continueOnError')
        create_new_team = dictionary.get('createNewTeam')
        objects = None
        if dictionary.get('objects') is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.object_ms_team_param.ObjectMsTeamParam.from_dictionary(structure))
        restore_original_owners = dictionary.get('restoreOriginalOwners')
        restore_to_original = dictionary.get('restoreToOriginal')
        target_ms_team = cohesity_management_sdk.models_v2.target_ms_team_param.TargetMsTeamParam.from_dictionary(dictionary.get('targetMsTeam')) if dictionary.get('targetMsTeam') else None
        target_ms_team_param = cohesity_management_sdk.models_v2.target_ms_team_param.TargetMsTeamParam.from_dictionary(dictionary.get('targetMsTeamParam')) if dictionary.get('targetMsTeamParam') else None
        target_team_full_name = dictionary.get('targetTeamFullName')
        target_team_name = dictionary.get('targetTeamName')
        target_team_nick_name = dictionary.get('targetTeamNickName')
        target_team_owner = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('targetTeamOwner')) if dictionary.get('targetTeamOwner') else None

        return cls(
            continue_on_error,
            create_new_team,
            objects,
            restore_original_owners,
            restore_to_original,
            target_ms_team,
            target_ms_team_param,
            target_team_full_name,
            target_team_name,
            target_team_nick_name,
            target_team_owner
        )