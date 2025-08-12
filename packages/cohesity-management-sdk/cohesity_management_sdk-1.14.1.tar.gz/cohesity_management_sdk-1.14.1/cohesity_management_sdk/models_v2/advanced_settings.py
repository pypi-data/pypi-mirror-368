# -*- coding: utf-8 -*-


class AdvancedSettings(object):

    """Implementation of the 'AdvancedSettings' model.

    This is used to regulate certain gflag values from the UI. The values
      passed by the user from the UI will be used for the respective gflags.

    Attributes:
        cloned_db_backup_status (AdvanceSettingsEnum): Whether to report error if SQL database is cloned.
        db_backup_if_not_online_status (AdvanceSettingsEnum): Whether to report error if SQL database is not online.
        missing_db_backup_status (AdvanceSettingsEnum): Fail the backup job when the database is missing. The database
          may be missing if it is deleted or corrupted.
        offline_restoring_db_backup_status (AdvanceSettingsEnum): Fail the backup job when database is offline or restoring.
        read_only_db_backup_status (AdvanceSettingsEnum): Whether to skip backup for read-only SQL databases.
        report_all_non_auto_protect_db_errors (AdvanceSettingsEnum): Whether to report error for all dbs in non-autoprotect jobs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cloned_db_backup_status":'clonedDbBackupStatus',
        "db_backup_if_not_online_status":'dbBackupIfNotOnlineStatus',
        "missing_db_backup_status":'missingDbBackupStatus',
        "offline_restoring_db_backup_status":'offlineRestoringDbBackupStatus',
        "read_only_db_backup_status":'readOnlyDbBackupStatus',
        "report_all_non_auto_protect_db_errors":'reportAllNonAutoprotectDbErrors'
    }

    def __init__(self,
                 cloned_db_backup_status=None,
                 db_backup_if_not_online_status=None,
                 missing_db_backup_status=None,
                 offline_restoring_db_backup_status=None,
                 read_only_db_backup_status=None,
                 report_all_non_auto_protect_db_errors=None):
        """Constructor for the AdvancedSettings class"""

        # Initialize members of the class
        self.cloned_db_backup_status = cloned_db_backup_status
        self.db_backup_if_not_online_status = db_backup_if_not_online_status
        self.missing_db_backup_status = missing_db_backup_status
        self.offline_restoring_db_backup_status = offline_restoring_db_backup_status
        self.read_only_db_backup_status = read_only_db_backup_status
        self.report_all_non_auto_protect_db_errors = report_all_non_auto_protect_db_errors



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
        cloned_db_backup_status = dictionary.get('clonedDbBackupStatus')
        db_backup_if_not_online_status = dictionary.get('dbBackupIfNotOnlineStatus')
        missing_db_backup_status = dictionary.get('missingDbBackupStatus')
        offline_restoring_db_backup_status = dictionary.get('offlineRestoringDbBackupStatus')
        read_only_db_backup_status = dictionary.get('readOnlyDbBackupStatus')
        report_all_non_auto_protect_db_errors = dictionary.get('reportAllNonAutoprotectDbErrors')

        # Return an object of this model
        return cls(cloned_db_backup_status,
                   db_backup_if_not_online_status,
                   missing_db_backup_status,
                   offline_restoring_db_backup_status,
                   read_only_db_backup_status,
                   report_all_non_auto_protect_db_errors)