# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.filename_pattern_to_directory
import cohesity_management_sdk.models_v2.multi_stage_restore_options
import cohesity_management_sdk.models_v2.host

class CommonSqlAppSourceConfig(object):

    """Implementation of the 'Common Sql App Source Config.' model.

    Specifies a common parameters used when restroring back to original or new
    source.

    Attributes:
        restore_time_usecs (long|int): Specifies the time in the past to which
            the Sql database needs to be restored. This allows for granular
            recovery of Sql databases. If this is not set, the Sql database
            will be restored from the full/incremental snapshot.
        secondary_data_files_dir_list (list of FilenamePatternToDirectory):
            Specifies the secondary data filename pattern and corresponding
            direcories of the DB. Secondary data files are optional and are
            user defined. The recommended file extention for secondary files
            is ".ndf". If this option is specified and the destination folders
            do not exist they will be automatically created.
        with_no_recovery (bool): Specifies the flag to bring DBs online or not
            after successful recovery. If this is passed as true, then it
            means DBs won't be brought online.
        keep_cdc (bool): Specifies whether to keep CDC (Change Data Capture)
            on recovered databases or not. If not passed, this is assumed to
            be true. If withNoRecovery is passed as true, then this field must
            not be set to true. Passing this field as true in this scenario
            will be a invalid request.
        overwriting_policy (OverwritingPolicyEnum): Specifies a policy to be
            used while recovering existing databases.
        multi_stage_restore_options (MultiStageRestoreOptions): Specifies the
            parameters related to multi stage Sql restore.
        native_recovery_with_clause (string): 'with_clause' contains 'with
            clause' to be used in native sql restore command. This is only
            applicable for database restore of native sql backup. Here user
            can specify multiple restore options. Example: 'WITH BUFFERCOUNT =
            575, MAXTRANSFERSIZE = 2097152'.
        replay_entire_last_log (bool): Specifies the option to set replay last
          log bit while creating the sql restore task and doing restore to latest
          point-in-time. If this is set to true, we will replay the entire last log
          without STOPAT.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "restore_time_usecs":'restoreTimeUsecs',
        "secondary_data_files_dir_list":'secondaryDataFilesDirList',
        "with_no_recovery":'withNoRecovery',
        "keep_cdc":'keepCdc',
        "multi_stage_restore_options":'multiStageRestoreOptions',
        "native_recovery_with_clause":'nativeRecoveryWithClause',
        "overwriting_policy":'overwritingPolicy',
        "replay_entire_last_log": 'replayEntireLastLog'
    }

    def __init__(self,
                 restore_time_usecs=None,
                 secondary_data_files_dir_list=None,
                 with_no_recovery=None,
                 keep_cdc=None,
                 multi_stage_restore_options=None,
                 native_recovery_with_clause=None,
                 overwriting_policy=None,
                 replay_entire_last_log=None):
        """Constructor for the CommonSqlAppSourceConfig class"""

        # Initialize members of the class
        self.restore_time_usecs = restore_time_usecs
        self.secondary_data_files_dir_list = secondary_data_files_dir_list
        self.with_no_recovery = with_no_recovery
        self.keep_cdc = keep_cdc
        self.multi_stage_restore_options = multi_stage_restore_options
        self.native_recovery_with_clause = native_recovery_with_clause
        self.overwriting_policy = overwriting_policy
        self.replay_entire_last_log = replay_entire_last_log


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
        restore_time_usecs = dictionary.get('restoreTimeUsecs')
        secondary_data_files_dir_list = None
        if dictionary.get("secondaryDataFilesDirList") is not None:
            secondary_data_files_dir_list = list()
            for structure in dictionary.get('secondaryDataFilesDirList'):
                secondary_data_files_dir_list.append(cohesity_management_sdk.models_v2.filename_pattern_to_directory.FilenamePatternToDirectory.from_dictionary(structure))
        with_no_recovery = dictionary.get('withNoRecovery')
        keep_cdc = dictionary.get('keepCdc')
        multi_stage_restore_options = cohesity_management_sdk.models_v2.multi_stage_restore_options.MultiStageRestoreOptions.from_dictionary(
            dictionary.get('multiStageRestoreOptions')) if dictionary.get('multiStageRestoreOptions') else None
        native_recovery_with_clause = dictionary.get('nativeRecoveryWithClause')
        overwriting_policy = dictionary.get('overwritingPolicy')
        replay_entire_last_log = dictionary.get('replayEntireLastLog')

        # Return an object of this model
        return cls(restore_time_usecs,
                   secondary_data_files_dir_list,
                   with_no_recovery,
                   keep_cdc,
                   multi_stage_restore_options,
                   native_recovery_with_clause,
                   overwriting_policy,
                   replay_entire_last_log)

class RecoverSqlAppNewSourceConfig(CommonSqlAppSourceConfig) :

        """Implementation of the 'Recover Sql App New Source Config.' model.

        Specifies the new destination Source configuration where the databases
        will be recovered.
        NOTE: This class inherits from 'CommonSqlAppSourceConfig'.

        Attributes:
            host (Host): Specifies the source id of target host where databases
                will be recovered. This source id can be a physical host or
                virtual machine.
            instance_name (string): Specifies an instance name of the Sql Server
                that should be used for restoring databases to.
            data_file_directory_location (string): Specifies the directory where
                to put the database data files. Missing directory will be
                automatically created.
            log_file_directory_location (string): Specifies the directory where to
                put the database log files. Missing directory will be
                automatically created.
            database_name (string): Specifies a new name for the restored
                database. If this field is not specified, then the original
                database will be overwritten after recovery.

        """

        # Create a mapping from Model property names to API property names
        _names = {
            "host"                          : 'host' ,
            "instance_name"                 : 'instanceName' ,
            "data_file_directory_location"  : 'dataFileDirectoryLocation' ,
            "log_file_directory_location"   : 'logFileDirectoryLocation' ,
            "database_name"                 : 'databaseName' ,
            "restore_time_usecs"            : 'restoreTimeUsecs' ,
            "secondary_data_files_dir_list" : 'secondaryDataFilesDirList' ,
            "with_no_recovery"              : 'withNoRecovery' ,
            "keep_cdc"                      : 'keepCdc' ,
            "overwriting_policy"            : 'overwritingPolicy' ,
            "multi_stage_restore_options"   : 'multiStageRestoreOptions' ,
            "native_recovery_with_clause"   : 'nativeRecoveryWithClause'
        }

        def __init__(self ,
                     host=None ,
                     instance_name=None ,
                     data_file_directory_location=None ,
                     log_file_directory_location=None ,
                     database_name=None ,
                     restore_time_usecs=None ,
                     secondary_data_files_dir_list=None ,
                     with_no_recovery=None ,
                     keep_cdc=None ,
                     overwriting_policy=None ,
                     multi_stage_restore_options=None ,
                     native_recovery_with_clause=None) :
            """Constructor for the RecoverSqlAppNewSourceConfig class"""

            # Initialize members of the class
            self.host = host
            self.instance_name = instance_name
            self.data_file_directory_location = data_file_directory_location
            self.log_file_directory_location = log_file_directory_location
            self.database_name = database_name

            # Call the constructor for the base class
            super(RecoverSqlAppNewSourceConfig , self).__init__(restore_time_usecs ,
                                                                secondary_data_files_dir_list ,
                                                                with_no_recovery ,
                                                                keep_cdc ,
                                                                overwriting_policy ,
                                                                multi_stage_restore_options ,
                                                                native_recovery_with_clause)

        @classmethod
        def from_dictionary(cls ,
                            dictionary) :
            """Creates an instance of this model from a dictionary

            Args:
                dictionary (dictionary): A dictionary representation of the object as
                obtained from the deserialization of the server's response. The keys
                MUST match property names in the API description.

            Returns:
                object: An instance of this structure class.

            """
            if dictionary is None :
                return None

            # Extract variables from the dictionary
            host = cohesity_management_sdk.models_v2.host.Host.from_dictionary(
                dictionary.get('host')) if dictionary.get('host') else None
            instance_name = dictionary.get('instanceName')
            data_file_directory_location = dictionary.get('dataFileDirectoryLocation')
            log_file_directory_location = dictionary.get('logFileDirectoryLocation')
            database_name = dictionary.get('databaseName')
            restore_time_usecs = dictionary.get('restoreTimeUsecs')
            secondary_data_files_dir_list = None
            if dictionary.get('secondaryDataFilesDirList') is not None :
                secondary_data_files_dir_list = list()
                for structure in dictionary.get('secondaryDataFilesDirList') :
                    secondary_data_files_dir_list.append(
                        cohesity_management_sdk.models_v2.filename_pattern_to_directory.FilenamePatternToDirectory.from_dictionary(
                            structure))
            with_no_recovery = dictionary.get('withNoRecovery')
            keep_cdc = dictionary.get('keepCdc')
            overwriting_policy = dictionary.get('overwritingPolicy')
            multi_stage_restore_options = cohesity_management_sdk.models_v2.multi_stage_restore_options.MultiStageRestoreOptions.from_dictionary(
                dictionary.get('multiStageRestoreOptions')) if dictionary.get('multiStageRestoreOptions') else None
            native_recovery_with_clause = dictionary.get('nativeRecoveryWithClause')

            # Return an object of this model
            return cls(host ,
                       instance_name ,
                       data_file_directory_location ,
                       log_file_directory_location ,
                       database_name ,
                       restore_time_usecs ,
                       secondary_data_files_dir_list ,
                       with_no_recovery ,
                       keep_cdc ,
                       overwriting_policy ,
                       multi_stage_restore_options ,
                       native_recovery_with_clause)

class RecoverSqlAppNewSourceConfig1(CommonSqlAppSourceConfig) :

        """Implementation of the 'Recover Sql App New Source Config.1' model.

        Specifies the additional Source configuration parameters when databases
        will be recovered to original location.
        NOTE: This class inherits from 'CommonSqlAppSourceConfig'.

        Attributes:
            data_file_directory_location (string): Specifies the directory where
                to put the database data files. Missing directory will be
                automatically created. If you are overwriting the existing
                database then this field will be ignored.
            log_file_directory_location (string): Specifies the directory where to
                put the database log files. Missing directory will be
                automatically created. If you are overwriting the existing
                database then this field will be ignored.
            capture_tail_logs (bool): Set this to true if tail logs are to be
                captured before the recovery operation. This is only applicable if
                database is not being renamed.
            new_database_name (string): Specifies a new name for the restored
                database. If this field is not specified, then the original
                database will be overwritten after recovery.

        """

        # Create a mapping from Model property names to API property names
        _names = {
            "data_file_directory_location"  : 'dataFileDirectoryLocation' ,
            "log_file_directory_location"   : 'logFileDirectoryLocation' ,
            "capture_tail_logs"             : 'captureTailLogs' ,
            "new_database_name"             : 'newDatabaseName' ,
            "restore_time_usecs"            : 'restoreTimeUsecs' ,
            "secondary_data_files_dir_list" : 'secondaryDataFilesDirList' ,
            "with_no_recovery"              : 'withNoRecovery' ,
            "keep_cdc"                      : 'keepCdc' ,
            "overwriting_policy"            : 'overwritingPolicy' ,
            "multi_stage_restore_options"   : 'multiStageRestoreOptions' ,
            "native_recovery_with_clause"   : 'nativeRecoveryWithClause'
        }

        def __init__(self ,
                     data_file_directory_location=None ,
                     log_file_directory_location=None ,
                     capture_tail_logs=None ,
                     new_database_name=None ,
                     restore_time_usecs=None ,
                     secondary_data_files_dir_list=None ,
                     with_no_recovery=None ,
                     keep_cdc=None ,
                     overwriting_policy=None ,
                     multi_stage_restore_options=None ,
                     native_recovery_with_clause=None) :
            """Constructor for the RecoverSqlAppNewSourceConfig1 class"""

            # Initialize members of the class
            self.data_file_directory_location = data_file_directory_location
            self.log_file_directory_location = log_file_directory_location
            self.capture_tail_logs = capture_tail_logs
            self.new_database_name = new_database_name

            # Call the constructor for the base class
            super(RecoverSqlAppNewSourceConfig1 , self).__init__(restore_time_usecs ,
                                                                 secondary_data_files_dir_list ,
                                                                 with_no_recovery ,
                                                                 keep_cdc ,
                                                                 overwriting_policy ,
                                                                 multi_stage_restore_options ,
                                                                 native_recovery_with_clause)

        @classmethod
        def from_dictionary(cls ,
                            dictionary) :
            """Creates an instance of this model from a dictionary

            Args:
                dictionary (dictionary): A dictionary representation of the object as
                obtained from the deserialization of the server's response. The keys
                MUST match property names in the API description.

            Returns:
                object: An instance of this structure class.

            """
            if dictionary is None :
                return None

            # Extract variables from the dictionary
            data_file_directory_location = dictionary.get('dataFileDirectoryLocation')
            log_file_directory_location = dictionary.get('logFileDirectoryLocation')
            capture_tail_logs = dictionary.get('captureTailLogs')
            new_database_name = dictionary.get('newDatabaseName')
            restore_time_usecs = dictionary.get('restoreTimeUsecs')
            secondary_data_files_dir_list = None
            if dictionary.get('secondaryDataFilesDirList') is not None :
                secondary_data_files_dir_list = list()
                for structure in dictionary.get('secondaryDataFilesDirList') :
                    secondary_data_files_dir_list.append(
                        cohesity_management_sdk.models_v2.filename_pattern_to_directory.FilenamePatternToDirectory.from_dictionary(
                            structure))
            with_no_recovery = dictionary.get('withNoRecovery')
            keep_cdc = dictionary.get('keepCdc')
            overwriting_policy = dictionary.get('overwritingPolicy')
            multi_stage_restore_options = cohesity_management_sdk.models_v2.multi_stage_restore_options.MultiStageRestoreOptions.from_dictionary(
                dictionary.get('multiStageRestoreOptions')) if dictionary.get('multiStageRestoreOptions') else None
            native_recovery_with_clause = dictionary.get('nativeRecoveryWithClause')

            # Return an object of this model
            return cls(data_file_directory_location ,
                       log_file_directory_location ,
                       capture_tail_logs ,
                       new_database_name ,
                       restore_time_usecs ,
                       secondary_data_files_dir_list ,
                       with_no_recovery ,
                       keep_cdc ,
                       overwriting_policy ,
                       multi_stage_restore_options ,
                       native_recovery_with_clause)