# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class OracleDisasterRecoveryParameters(object):
    """Implementation of the 'OracleDisasterRecoveryParameters' model.

    Specifies the parameters that are needed for Disaster Recovery of a database to its production configuration.

    Attributes:
        cleanup_original_db_files (bool): Specifies whether to cleanup the original database files or to do precheck to ensure no conflicting files exists. Recovery will fail if there are any conflicting files.
        is_disaster_recovery (bool): Specifies whether the recovery is of type Disaster Recovery.
        rename_database_asm_directory (bool): Whether to rename the database ASM directory. If false, the adapter will leave the database files and continue with clone and migration of datafiles. This might cause extra files left behind on the Oracle host from the existing database instance.
    """

    _names = {
        "cleanup_original_db_files":"cleanupOriginalDbFiles",
        "is_disaster_recovery":"isDisasterRecovery",
        "rename_database_asm_directory":"renameDatabaseAsmDirectory",
    }

    def __init__(self,
                 cleanup_original_db_files=None,
                 is_disaster_recovery=None,
                 rename_database_asm_directory=None):
        """Constructor for the OracleDisasterRecoveryParameters class"""

        self.cleanup_original_db_files = cleanup_original_db_files
        self.is_disaster_recovery = is_disaster_recovery
        self.rename_database_asm_directory = rename_database_asm_directory


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

        cleanup_original_db_files = dictionary.get('cleanupOriginalDbFiles')
        is_disaster_recovery = dictionary.get('isDisasterRecovery')
        rename_database_asm_directory = dictionary.get('renameDatabaseAsmDirectory')

        return cls(
            cleanup_original_db_files,
            is_disaster_recovery,
            rename_database_asm_directory
        )