# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.pre_and_post_script_params
import cohesity_management_sdk.models_v2.filter
import cohesity_management_sdk.models_v2.advanced_settings

class CommonMSSQLProtectionGroupRequestParams(object):

    """Implementation of the 'Common MSSQL Protection Group Request Params.' model.

    Specifies the common params to create a MSSQL Protection Group.

    Attributes:
        user_db_backup_preference_type (UserDbBackupPreferenceTypeEnum):
            Specifies the preference type for backing up user databases on the
            host.
        backup_system_dbs (bool): Specifies whether to backup system
            databases. If not specified then parameter is set to true.
        use_aag_preferences_from_server (bool): Specifies whether or not the
            AAG backup preferences specified on the SQL Server host should be
            used.
        aag_backup_preference_type (AagBackupPreferenceType1Enum): Specifies
            the preference type for backing up databases that are part of an
            AAG. If not specified, then default preferences of the AAG server
            are applied. This field wont be applicable if user DB preference
            is set to skip AAG databases.
        advanced_settings (AdvancedSettings): This is used to regulate certain gflag values from the UI. The
          values passed by the user from the UI will be used for the respective gflags.
        full_backups_copy_only (bool): Specifies whether full backups should
            be copy-only.
        pre_post_script (PreAndPostScriptParams): Specifies the params for pre
            and post scripts.
        log_backup_num_streams (long|int): Specifies the number of streams to be used for log backups.
        log_backup_with_clause (string): Specifies the WithClause to be used for log backups.
        exclude_filters (list of Filter): Specifies the list of exclusion
            filters applied during the group creation or edit. These exclusion
            filters can be wildcard supported strings or regular expressions.
            Objects satisfying the will filters will be excluded during backup
            and also auto protected objects will be ignored if filtered by any
            of the filters.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "user_db_backup_preference_type":'userDbBackupPreferenceType',
        "backup_system_dbs":'backupSystemDbs',
        "use_aag_preferences_from_server":'useAagPreferencesFromServer',
        "aag_backup_preference_type":'aagBackupPreferenceType',
        "advanced_settings":'advancedSettings',
        "full_backups_copy_only":'fullBackupsCopyOnly',
        "pre_post_script":'prePostScript',
        "log_backup_num_streams":'logBackupNumStreams',
        "log_backup_with_clause":'logBackupWithClause',
        "exclude_filters":'excludeFilters'
    }

    def __init__(self,
                 user_db_backup_preference_type=None,
                 backup_system_dbs=None,
                 use_aag_preferences_from_server=None,
                 aag_backup_preference_type=None,
                 advanced_settings=None,
                 full_backups_copy_only=None,
                 pre_post_script=None,
                 log_backup_num_streams=None,
                 log_backup_with_clause=None,
                 exclude_filters=None):
        """Constructor for the CommonMSSQLProtectionGroupRequestParams class"""

        # Initialize members of the class
        self.user_db_backup_preference_type = user_db_backup_preference_type
        self.backup_system_dbs = backup_system_dbs
        self.use_aag_preferences_from_server = use_aag_preferences_from_server
        self.aag_backup_preference_type = aag_backup_preference_type
        self.advanced_settings = advanced_settings
        self.full_backups_copy_only = full_backups_copy_only
        self.pre_post_script = pre_post_script
        self.log_backup_num_streams = log_backup_num_streams
        self.log_backup_with_clause = log_backup_with_clause
        self.exclude_filters = exclude_filters


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
        user_db_backup_preference_type = dictionary.get('userDbBackupPreferenceType')
        backup_system_dbs = dictionary.get('backupSystemDbs')
        use_aag_preferences_from_server = dictionary.get('useAagPreferencesFromServer')
        aag_backup_preference_type = dictionary.get('aagBackupPreferenceType')
        advanced_settings = cohesity_management_sdk.models_v2.advanced_settings.AdvancedSettings.from_dictionary(dictionary.get('advancedSettings')) if dictionary.get('advancedSettings') else None
        full_backups_copy_only = dictionary.get('fullBackupsCopyOnly')
        pre_post_script = cohesity_management_sdk.models_v2.pre_and_post_script_params.PreAndPostScriptParams.from_dictionary(dictionary.get('prePostScript')) if dictionary.get('prePostScript') else None
        log_backup_num_streams = dictionary.get('logBackupNumStreams')
        log_backup_with_clause = dictionary.get('logBackupWithClause')
        exclude_filters = None
        if dictionary.get("excludeFilters") is not None:
            exclude_filters = list()
            for structure in dictionary.get('excludeFilters'):
                exclude_filters.append(cohesity_management_sdk.models_v2.filter.Filter.from_dictionary(structure))

        # Return an object of this model
        return cls(user_db_backup_preference_type,
                   backup_system_dbs,
                   use_aag_preferences_from_server,
                   aag_backup_preference_type,
                   advanced_settings,
                   full_backups_copy_only,
                   pre_post_script,
                   log_backup_num_streams,
                   log_backup_with_clause,
                   exclude_filters)