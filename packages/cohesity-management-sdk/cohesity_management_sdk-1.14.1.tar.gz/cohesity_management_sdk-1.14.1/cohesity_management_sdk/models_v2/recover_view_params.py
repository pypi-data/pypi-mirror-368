# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.oracle_protection_group_database_node_channel
import cohesity_management_sdk.models_v2.shell_key_value_pair
import cohesity_management_sdk.models_v2.oracle_archive_log_info
import cohesity_management_sdk.models_v2.recover_oracle_granular_restore_information
import cohesity_management_sdk.models_v2.oracle_recovery_validation_info
import cohesity_management_sdk.models_v2.restore_sp_file_or_p_file_info

class RecoverViewParams(object):

    """Implementation of the 'RecoverViewParams' model.

    Specifies recovery parameters when recovering to a view.

    Attributes:
        restore_spfile_or_p_file_info (RestoreSpfileOrPfileInfo): Specifies parameters related to spfile/pfile restore.
        use_scn_for_restore (bool): Specifies whether database recovery performed should use scn
          value or not.
        oracle_archive_log_info (OracleArchiveLogInfo): Specifies Range in Time, Scn or Sequence to restore archive logs
          of a DB.
        oracle_recovery_validation_info (OracleRecoveryValidationInfo): Specifies parameters related to Oracle Recovery Validation.
        view_mount_path (string): Specifies the directory where cohesity view
            for app recovery will be mounted.
        restore_time_usecs (long|int): Specifies the time in the past to which
            the Oracle db needs to be restored. This allows for granular
            recovery of Oracle databases. If this is not set, the Oracle db
            will be restored from the full/incremental snapshot.
        db_channels (list of OracleProtectionGroupDatabaseNodeChannel):
            Specifies the Oracle database node channels info. If not
            specified, the default values assigned by the server are applied
            to all the databases.
        recovery_mode (bool): Specifies if database should be left in recovery
            mode.
        shell_evironment_vars (list of ShellKeyValuePair): Specifies key value
            pairs of shell variables which defines the restore shell
            environment.
        granular_restore_info (RecoverOracleGranularRestoreInformation):
            Specifies information about list of objects (PDBs) to restore.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "restore_spfile_or_p_file_info":'restoreSpfileOrPfileInfo',
        "use_scn_for_restore":'useScnForRestore',
        "oracle_archive_log_info":'oracleArchiveLogInfo',
        "oracle_recovery_validation_info":'oracleRecoveryValidationInfo',
        "view_mount_path":'viewMountPath',
        "restore_time_usecs":'restoreTimeUsecs',
        "db_channels":'dbChannels',
        "recovery_mode":'recoveryMode',
        "shell_evironment_vars":'shellEvironmentVars',
        "granular_restore_info":'granularRestoreInfo'
    }

    def __init__(self,
                 restore_spfile_or_p_file_info=None,
                 use_scn_for_restore=None,
                 oracle_archive_log_info=None,
                 oracle_recovery_validation_info=None,
                 view_mount_path=None,
                 restore_time_usecs=None,
                 db_channels=None,
                 recovery_mode=None,
                 shell_evironment_vars=None,
                 granular_restore_info=None):
        """Constructor for the RecoverViewParams class"""

        # Initialize members of the class
        self.restore_spfile_or_p_file_info = restore_spfile_or_p_file_info
        self.use_scn_for_restore = use_scn_for_restore
        self.oracle_archive_log_info = oracle_archive_log_info
        self.oracle_recovery_validation_info = oracle_recovery_validation_info
        self.view_mount_path = view_mount_path
        self.restore_time_usecs = restore_time_usecs
        self.db_channels = db_channels
        self.recovery_mode = recovery_mode
        self.shell_evironment_vars = shell_evironment_vars
        self.granular_restore_info = granular_restore_info


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
        restore_spfile_or_p_file_info = cohesity_management_sdk.models_v2.restore_sp_file_or_p_file_info.RestoreSpfileOrPfileInfo.from_dictionary(
            dictionary.get('restoreSpfileOrPfileInfo')) if dictionary.get('restoreSpfileOrPfileInfo') else None
        use_scn_for_restore = dictionary.get('useScnForRestore')
        oracle_archive_log_info = cohesity_management_sdk.models_v2.oracle_archive_log_info.OracleArchiveLogInfo.from_dictionary(
            dictionary.get('oracleArchiveLogInfo')) if dictionary.get('oracleArchiveLogInfo') else None
        oracle_recovery_validation_info = cohesity_management_sdk.models_v2.oracle_recovery_validation_info.OracleRecoveryValidationInfo.from_dictionary(
            dictionary.get('oracleRecoveryValidationInfo')) if dictionary.get('oracleRecoveryValidationInfo') else None
        view_mount_path = dictionary.get('viewMountPath')
        restore_time_usecs = dictionary.get('restoreTimeUsecs')
        db_channels = None
        if dictionary.get("dbChannels") is not None:
            db_channels = list()
            for structure in dictionary.get('dbChannels'):
                db_channels.append(cohesity_management_sdk.models_v2.oracle_protection_group_database_node_channel.OracleProtectionGroupDatabaseNodeChannel.from_dictionary(structure))
        recovery_mode = dictionary.get('recoveryMode')
        shell_evironment_vars = None
        if dictionary.get("shellEvironmentVars") is not None:
            shell_evironment_vars = list()
            for structure in dictionary.get('shellEvironmentVars'):
                shell_evironment_vars.append(cohesity_management_sdk.models_v2.shell_key_value_pair.ShellKeyValuePair.from_dictionary(structure))
        granular_restore_info = cohesity_management_sdk.models_v2.recover_oracle_granular_restore_information.RecoverOracleGranularRestoreInformation.from_dictionary(dictionary.get('granularRestoreInfo')) if dictionary.get('granularRestoreInfo') else None

        # Return an object of this model
        return cls(restore_spfile_or_p_file_info,
                   use_scn_for_restore,
                   oracle_archive_log_info,
                   oracle_recovery_validation_info,
                   view_mount_path,
                   restore_time_usecs,
                   db_channels,
                   recovery_mode,
                   shell_evironment_vars,
                   granular_restore_info)