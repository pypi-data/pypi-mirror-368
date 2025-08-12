# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.download_file_and_folder_params
import cohesity_management_sdk.models_v2.download_chat_params
import cohesity_management_sdk.models_v2.recover_one_drive_params_2
import cohesity_management_sdk.models_v2.recover_mailbox_params_2
import cohesity_management_sdk.models_v2.recover_ms_teams_params
import  cohesity_management_sdk.models_v2.recover_ms_group_params
import cohesity_management_sdk.models_v2.recover_public_folders_params
import cohesity_management_sdk.models_v2.recover_site_params

class RecoverOffice365EnvironmentParams(object):

    """Implementation of the 'Recover Office 365 environment params.' model.

    Specifies the recovery options specific to Office 365 environment.

    Attributes:
        download_chats_params (DownloadChatParams): Specifies the download chats specific parameters for downloading
          posts for a team/channel or downloading private chats for a user.
        download_file_and_folder_params (DownloadFileAndFolderParams): Specifies the recovery information to download files and folders.
          For instance, downloading mailbox items as PST.
        recover_ms_group_params (RecoverMsGroupParams): Specifies the parameters to recover Microsoft 365 Group.
        recover_ms_team_params (RecoverMsTeamParams): Specifies the parameters to recover Microsoft 365 Teams.
        recover_site_params (RecoverSiteParams): Specifies the parameters to recover Microsoft Office 365 Sharepoint
          Site.
        objects (list of CommonRecoverObjectSnapshotParams): Specifies the
            list of recover Object parameters.
        recovery_action (RecoveryAction13Enum): Specifies the type of recovery
            action to be performed.
        recover_one_drive_params (RecoverOneDriveParams2): Specifies the
            parameters to recover Office 365 One Drive.
        recover_mailbox_params (RecoverMailboxParams2): Specifies the
            parameters to recover Office 365 Mailbox.
        recover_public_folders_params (RecoverPublicFoldersParams): Specifies
            the parameters to recover Office 365 Public Folders.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_action":'recoveryAction',
        "download_chats_params":'downloadChatsParams',
        "download_file_and_folder_params":'downloadFileAndFolderParams',
        "recover_ms_group_params":'recoverMsGroupParams',
        "recover_ms_team_params":'recoverMsTeamParams',
        "recover_site_params":'recoverSiteParams',
        "objects":'objects',
        "recover_one_drive_params":'recoverOneDriveParams',
        "recover_mailbox_params":'recoverMailboxParams',
        "recover_public_folders_params":'recoverPublicFoldersParams'
    }

    def __init__(self,
                 recovery_action=None,
                 download_chats_params=None,
                 download_file_and_folder_params=None,
                 recover_ms_group_params=None,
                 recover_ms_team_params=None,
                 recover_site_params=None,
                 objects=None,
                 recover_one_drive_params=None,
                 recover_mailbox_params=None,
                 recover_public_folders_params=None):
        """Constructor for the RecoverOffice365EnvironmentParams class"""

        # Initialize members of the class
        self.recovery_action = recovery_action
        self.download_chats_params = download_chats_params
        self.download_file_and_folder_params = download_file_and_folder_params
        self.recover_ms_group_params = recover_ms_group_params
        self.recover_ms_team_params = recover_ms_team_params
        self.recover_site_params = recover_site_params
        self.objects = objects
        self.recover_one_drive_params = recover_one_drive_params
        self.recover_mailbox_params = recover_mailbox_params
        self.recover_public_folders_params = recover_public_folders_params


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
        recovery_action = dictionary.get('recoveryAction')
        download_chats_params = cohesity_management_sdk.models_v2.download_chat_params.DownloadChatParams.from_dictionary(dictionary.get('downloadChatsParams')) if dictionary.get('downloadChatsParams') else None
        download_file_and_folder_params = cohesity_management_sdk.models_v2.download_file_and_folder_params.DownloadFileAndFolderParams.from_dictionary(dictionary.get('downloadFileAndFolderParams')) if dictionary.get('downloadFileAndFolderParams') else None
        recover_ms_group_params = cohesity_management_sdk.models_v2.recover_ms_group_params.RecoverMsGroupParams.from_dictionary(dictionary.get('recoverMsGroupParams')) if dictionary.get('recoverMsGroupParams') else None
        recover_ms_team_params = cohesity_management_sdk.models_v2.recover_ms_teams_params.RecoverMsTeamParams.from_dictionary(dictionary.get('recoverMsTeamParams')) if dictionary.get('recoverMsTeamParams') else None
        recover_site_params = cohesity_management_sdk.models_v2.recover_site_params.RecoverSiteParams.from_dictionary(dictionary.get('recoverSiteParams')) if dictionary.get('recoverSiteParams') else None
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(structure))
        recover_one_drive_params = cohesity_management_sdk.models_v2.recover_one_drive_params_2.RecoverOneDriveParams2.from_dictionary(dictionary.get('recoverOneDriveParams')) if dictionary.get('recoverOneDriveParams') else None
        recover_mailbox_params = cohesity_management_sdk.models_v2.recover_mailbox_params_2.RecoverMailboxParams2.from_dictionary(dictionary.get('recoverMailboxParams')) if dictionary.get('recoverMailboxParams') else None
        recover_public_folders_params = cohesity_management_sdk.models_v2.recover_public_folders_params.RecoverPublicFoldersParams.from_dictionary(dictionary.get('recoverPublicFoldersParams')) if dictionary.get('recoverPublicFoldersParams') else None

        # Return an object of this model
        return cls(recovery_action,
                   download_chats_params,
                   download_file_and_folder_params,
                   recover_ms_group_params,
                   recover_ms_team_params,
                   recover_site_params,
                   objects,
                   recover_one_drive_params,
                   recover_mailbox_params,
                   recover_public_folders_params)