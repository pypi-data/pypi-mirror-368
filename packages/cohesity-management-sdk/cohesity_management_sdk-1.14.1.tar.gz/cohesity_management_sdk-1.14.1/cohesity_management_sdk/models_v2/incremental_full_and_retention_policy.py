# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.incremental_backup_schedule_and_retention
import cohesity_management_sdk.models_v2.full_backup_schedule_and_retention
import cohesity_management_sdk.models_v2.full_schedule_and_retention
import cohesity_management_sdk.models_v2.primary_backup_target
import cohesity_management_sdk.models_v2.retention

class IncrementalFullAndRetentionPolicy(object):

    """Implementation of the 'Incremental, Full and Retention Policy.' model.

    Specifies the Incremental and Full policy settings and also the common
    Retention policy settings."

    Attributes:
        incremental (IncrementalBackupScheduleAndRetention): Specifies
            incremental backup settings for a Protection Group.
        full (FullBackupScheduleAndRetention): Specifies full backup settings
            for a Protection Group.
        full_backups (list of FullScheduleAndRetention): Specifies multiple schedules and retentions for full backup.
          Specify either of the 'full' or 'fullBackups' values. Its recommended to
          use 'fullBaackups' value since 'full' will be deprecated after few releases.
        primary_backup_target (PrimaryBackupTarget): Specifies the primary backup target settings for regular backups.
          Specifying this field shows that instead of local backups on Cohesity cluster,
          primary backup location is different such as Cloud Archives like s3 or azure.
        retention (Retention): Specifies the retention of a backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "incremental":'incremental',
        "full":'full',
        "full_backups":'fullBackups',
        "primary_backup_target":'primaryBackupTarget',
        "retention":'retention'
    }

    def __init__(self,
                 incremental=None,
                 full=None,
                 full_backups=None,
                 primary_backup_target=None,
                 retention=None):
        """Constructor for the IncrementalFullAndRetentionPolicy class"""

        # Initialize members of the class
        self.incremental = incremental
        self.full = full
        self.full_backups = full_backups
        self.primary_backup_target = primary_backup_target
        self.retention = retention


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
        incremental = cohesity_management_sdk.models_v2.incremental_backup_schedule_and_retention.IncrementalBackupScheduleAndRetention.from_dictionary(dictionary.get('incremental')) if dictionary.get('incremental') else None
        full = cohesity_management_sdk.models_v2.full_backup_schedule_and_retention.FullBackupScheduleAndRetention.from_dictionary(dictionary.get('full')) if dictionary.get('full') else None
        full_backups = None
        if dictionary.get("fullBackups") is not None:
            full_backups = list()
            for structure in dictionary.get('fullBackups'):
                full_backups.append(cohesity_management_sdk.models_v2.full_schedule_and_retention.FullScheduleAndRetention.from_dictionary(structure))
        primary_backup_target = cohesity_management_sdk.models_v2.primary_backup_target.PrimaryBackupTarget.from_dictionary(dictionary.get('primaryBackupTarget')) if dictionary.get('primaryBackupTarget') else None
        retention = cohesity_management_sdk.models_v2.retention.Retention.from_dictionary(
            dictionary.get('retention')) if dictionary.get('retention') else None


        # Return an object of this model
        return cls(
                   incremental,
                   full,
                   full_backups,
                   primary_backup_target,
                   retention,)