# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_sql_app_snapshot_params
import cohesity_management_sdk.models_v2.vlan_config_1
import cohesity_management_sdk.models_v2.archival_target
import cohesity_management_sdk.models_v2.aag_info
import cohesity_management_sdk.models_v2.host_information
import cohesity_management_sdk.models_v2.archival_target_tier_info

class RecoverSqlDBParams(object):

    """Implementation of the 'Recover Sql DB params.' model.

    Specifies the parameters to recover Sql databases.

    Attributes:
        usage_type (UsageTypeEnum): Specifies the usage type for the target.
        tier_settings (ArchivalTargetTierInfo): Specifies the tier level settings configured with archival target.
          This will be specified if the run is a CAD run.
        target_id (long|int): Specifies the archival target ID.
        target_name (string): Specifies the archival target name.
        target_type (TargetTypeEnum): Specifies the archival target type.
        ownership_context (OwnershipContextEnum): Specifies the ownership context for the target.
        archival_task_id (string): Specifies the archival task id. This is a protection group UID
          which only applies when archival type is 'Tape'.
        target_environment (string): Specifies the environment of the recovery
            target. The corresponding params below must be filled out.
        sql_target_params (RecoverSqlAppSnapshotParams): Specifies the params
            for recovering to a sql host. Provided sql backup should be
            recovered to same type of target host. For Example: If you have
            sql backup taken from a physical host then that should be
            recovered to physical host only.
        aag_info (AAGInfo): Specifies the Always on Avalibility (AAG) information if associated
          with the SQL Object.
        host_info (HostInformation): Specifies the host information for the SQL object. Includes details
          of Host object such as VM or Physical server.
        is_encrypted (bool): Specifies whether the database is TDE enabled.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "usage_type":'usageType',
        "tier_settings":'tierSettings',
        "target_id":'targetId',
        "target_name":'targetName',
        "target_type":'targetType',
        "ownership_context":'ownershipContext',
        "archival_task_id":'archivalTaskId',
        "target_environment":'targetEnvironment',
        "sql_target_params":'sqlTargetParams',
        "aag_info":'aagInfo',
        "host_info":'hostInfo',
        "is_encrypted":'isEncrypted'
    }

    def __init__(self,
                 usage_type=None,
                 tier_settings=None,
                 target_id=None,
                 target_name=None,
                 target_type=None,
                 ownership_context=None,
                 archival_task_id=None,
                 target_environment='kSQL',
                 sql_target_params=None,
                 aag_info=None,
                 host_info=None,
                 is_encrypted=None):
        """Constructor for the RecoverSqlDBParams class"""

        # Initialize members of the class
        self.usage_type = usage_type
        self.tier_settings = tier_settings
        self.target_id = target_id
        self.target_name = target_name
        self.target_type = target_type
        self.ownership_context = ownership_context
        self.archival_task_id = archival_task_id
        self.target_environment = target_environment
        self.sql_target_params = sql_target_params
        self.aag_info = aag_info
        self.host_info = host_info
        self.is_encrypted = is_encrypted


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
        usage_type = dictionary.get('usageType')
        tier_settings = cohesity_management_sdk.models_v2.archival_target_tier_info.ArchivalTargetTierInfo.from_dictionary(
            dictionary.get('tierSettings')) if dictionary.get('tierSettings') else None
        target_id = dictionary.get('targetId')
        target_name = dictionary.get('targetName')
        target_type = dictionary.get('targetType')
        ownership_context = dictionary.get('ownershipContext')
        archival_task_id = dictionary.get('archivalTaskId')
        target_environment = dictionary.get("targetEnvironment") if dictionary.get("targetEnvironment") else 'kSQL'
        sql_target_params = cohesity_management_sdk.models_v2.recover_sql_app_snapshot_params.RecoverSqlAppSnapshotParams.from_dictionary(dictionary.get('sqlTargetParams')) if dictionary.get('sqlTargetParams') else None
        aag_info = cohesity_management_sdk.models_v2.aag_info.AAGInfo.from_dictionary(
            dictionary.get('aagInfo')) if dictionary.get('aagInfo') else None
        host_info = cohesity_management_sdk.models_v2.host_information.HostInformation.from_dictionary(
            dictionary.get('hostInfo')) if dictionary.get('hostInfo') else None
        is_encrypted = dictionary.get('isEncrypted')

        # Return an object of this model
        return cls(usage_type,
                   tier_settings,
                   target_id,
                   target_name,
                   target_type,
                   ownership_context,
                   archival_task_id,
                   target_environment,
                   sql_target_params,
                   aag_info,
                   host_info,
                   is_encrypted)