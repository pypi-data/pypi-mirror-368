# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.filtering_policy_proto

class PhysicalBackupEnvParams(object):

    """Implementation of the 'PhysicalBackupEnvParams' model.

    Message to capture any additional backup params for a Physical
    environment.

    Attributes:
        cobmr_backup (bool): Whether CoBMR backup is enabled. If true,
            Cristie executables will be run
            in agent so that bare metal restore can be performed
        enable_incremental_backup_after_restart (bool): If this is set to
            true, then incremental backup will be performed after the server
            restarts, otherwise a full-backup will be done. NOTE: This is
            applicable to windows host environments.
        filtering_policy (FilteringPolicyProto): Proto to encapsulate the
            filtering policy for backup objects like files or directories. If
            an object is not matched by any of the 'allow_filters', it will be
            excluded in the backup. If an object is matched by one of the
            'deny_filters', it will always be excluded in the backup.
            Basically 'deny_filters' overwrite 'allow_filters' if they both
            match the same object. Currently we only support two kinds of
            filter: prefix which always starts with '/', or postfix which
            always starts with '*' (cannot be "*" only). We don't support
            regular expression right now. A concrete example is: Allow
            filters: "/" Deny filters: "/tmp", "*.mp4" Using such a policy
            will include everything under the root directory except the /tmp
            directory and all the mp4 files.
        vss_excluded_writers (list of string): List of VSS writers that are
            excluded.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cobmr_backup": 'cobmrBackup',
        "enable_incremental_backup_after_restart":'enableIncrementalBackupAfterRestart',
        "filtering_policy":'filteringPolicy',
        "vss_excluded_writers": 'vssExcludedWriters'
    }

    def __init__(self,
                 cobmr_backup=None,
                 enable_incremental_backup_after_restart=None,
                 filtering_policy=None,
                 vss_excluded_writers=None):
        """Constructor for the PhysicalBackupEnvParams class"""

        # Initialize members of the class
        self.cobmr_backup = cobmr_backup
        self.enable_incremental_backup_after_restart = enable_incremental_backup_after_restart
        self.filtering_policy = filtering_policy
        self.vss_excluded_writers = vss_excluded_writers


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
        cobmr_backup = dictionary.get('cobmrBackup')
        enable_incremental_backup_after_restart = dictionary.get('enableIncrementalBackupAfterRestart')
        filtering_policy = cohesity_management_sdk.models.filtering_policy_proto.FilteringPolicyProto.from_dictionary(dictionary.get('filteringPolicy')) if dictionary.get('filteringPolicy') else None
        vss_excluded_writers = dictionary.get('vssExcludedWriters')

        # Return an object of this model
        return cls(cobmr_backup,
                   enable_incremental_backup_after_restart,
                   filtering_policy,
                   vss_excluded_writers)


