# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models_v2.onedrive_backup_params
import cohesity_management_sdk.models_v2.outlook_backup_params

class O365EnvJobParams(object):
    """Implementation of the 'O365EnvJobParams' model.

    Specifies job parameters applicable for all 'kVMware' Environment type Protection Sources in a Protection Job.

    Attributes:
        onedrive_backup_params (OnedriveBackupParams): Specifies OneDrive backup parameters.
        outlook_backup_params (OutlookBackupParams): Specifies Outlook backup parameters.
    """

    _names = {
        "onedrive_backup_params":"onedriveBackupParams",
        "outlook_backup_params":"outlookBackupParams",
    }

    def __init__(self,
                 onedrive_backup_params=None,
                 outlook_backup_params=None):
        """Constructor for the O365EnvJobParams class"""

        self.onedrive_backup_params = onedrive_backup_params
        self.outlook_backup_params = outlook_backup_params


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

        onedrive_backup_params = cohesity_management_sdk.models_v2.onedrive_backup_params.OnedriveBackupParams.from_dictionary(dictionary.get('onedriveBackupParams')) if dictionary.get('onedriveBackupParams') else None
        outlook_backup_params = cohesity_management_sdk.models_v2.outlook_backup_params.OutlookBackupParams.from_dictionary(dictionary.get('outlookBackupParams')) if dictionary.get('outlookBackupParams') else None

        return cls(
            onedrive_backup_params,
            outlook_backup_params
        )