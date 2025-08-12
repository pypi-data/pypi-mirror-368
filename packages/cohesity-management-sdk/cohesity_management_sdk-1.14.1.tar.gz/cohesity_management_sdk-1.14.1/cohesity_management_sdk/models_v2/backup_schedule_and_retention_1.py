# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.incremental_full_and_retention_policy_1
import cohesity_management_sdk.models_v2.log_backup_databases_schedule_and_retention_2
import cohesity_management_sdk.models_v2.bmr_backup_physical_schedule_and_retention_2
import cohesity_management_sdk.models_v2.continious_data_protection_cdp_policy_2

class BackupScheduleAndRetention1(object):

    """Implementation of the 'Backup Schedule and Retention.1' model.

    Specifies the backup schedule and retentions of a Protection Policy.

    Attributes:
        regular (IncrementalFullAndRetentionPolicy1): Specifies the
            Incremental and Full policy settings and also the common Retention
            policy settings."
        log (LogBackupDatabasesScheduleAndRetention2): Specifies log backup
            settings for a Protection Group.
        bmr (BMRBackupPhysicalScheduleAndRetention2): Specifies the BMR
            schedule in case of physical source protection.
        cdp (ContiniousDataProtectionCDPPolicy2): Specifies CDP (Continious
            Data Protection) backup settings for a Protection Group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "regular":'regular',
        "log":'log',
        "bmr":'bmr',
        "cdp":'cdp'
    }

    def __init__(self,
                 regular=None,
                 log=None,
                 bmr=None,
                 cdp=None):
        """Constructor for the BackupScheduleAndRetention1 class"""

        # Initialize members of the class
        self.regular = regular
        self.log = log
        self.bmr = bmr
        self.cdp = cdp


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
        regular = cohesity_management_sdk.models_v2.incremental_full_and_retention_policy_1.IncrementalFullAndRetentionPolicy1.from_dictionary(dictionary.get('regular')) if dictionary.get('regular') else None
        log = cohesity_management_sdk.models_v2.log_backup_databases_schedule_and_retention_2.LogBackupDatabasesScheduleAndRetention2.from_dictionary(dictionary.get('log')) if dictionary.get('log') else None
        bmr = cohesity_management_sdk.models_v2.bmr_backup_physical_schedule_and_retention_2.BMRBackupPhysicalScheduleAndRetention2.from_dictionary(dictionary.get('bmr')) if dictionary.get('bmr') else None
        cdp = cohesity_management_sdk.models_v2.continious_data_protection_cdp_policy_2.ContiniousDataProtectionCDPPolicy2.from_dictionary(dictionary.get('cdp')) if dictionary.get('cdp') else None

        # Return an object of this model
        return cls(regular,
                   log,
                   bmr,
                   cdp)


