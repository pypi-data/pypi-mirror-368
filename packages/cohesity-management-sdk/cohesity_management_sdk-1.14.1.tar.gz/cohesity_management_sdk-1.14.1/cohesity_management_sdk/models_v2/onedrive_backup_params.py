# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models_v2.file_filtering_policy

class OnedriveBackupParams(object):
    """Implementation of the 'OnedriveBackupParams' model.

    Specifies OneDrive job parameters applicable for all Office365 Environment type Protection Sources in a Protection group.

    Attributes:
        file_path_filter (FileFilteringPolicy): Specifies filters on the backup objects like files and directories. Specifying filters decide which objects within a source should be backed up. If this field is not specified, then all of the objects within the source will be backed up.
        should_backup_onedrive (bool): TODO: type description here.
    """

    _names = {
        "file_path_filter":"filePathFilter",
        "should_backup_onedrive":"shouldBackupOnedrive",
    }

    def __init__(self,
                 file_path_filter=None,
                 should_backup_onedrive=None):
        """Constructor for the OnedriveBackupParams class"""

        self.file_path_filter = file_path_filter
        self.should_backup_onedrive = should_backup_onedrive


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

        file_path_filter = cohesity_management_sdk.models_v2.file_filtering_policy.FileFilteringPolicy.from_dictionary(dictionary.get('filePathFilter')) if dictionary.get('filePathFilter') else None
        should_backup_onedrive = dictionary.get('shouldBackupOnedrive')

        return cls(
            file_path_filter,
            should_backup_onedrive
        )