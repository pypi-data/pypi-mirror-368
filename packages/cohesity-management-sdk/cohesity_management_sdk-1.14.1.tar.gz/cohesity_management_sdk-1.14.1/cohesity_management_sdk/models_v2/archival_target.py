# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.archival_target_tier_info

class ArchivalTarget(object):

    """Implementation of the 'Archival target.' model.

    Specifies archival target summary information.

    Attributes:
        archival_task_id (string): Specifies the archival task id. This is a
            protection group UID which only applies when archival type is
            'Tape'.
        ownership_context (ownershipContext2Enum): Specifies the ownership context for the target.
        target_id (long|int): Specifies the archival target ID.
        target_name (string): Specifies the archival target name.
        target_type (TargetType1Enum): Specifies the archival target type.
        tier_settings (ArchivalTargetTierInfo): Specifies the tier level settings configured with archival target.
          This will be specified if the run is a CAD run.
        usage_type (UsageTypeEnum): Specifies the usage type for the target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "archival_task_id":'archivalTaskId',
        "ownership_context":'ownershipContext',
        "target_id":'targetId',
        "target_name":'targetName',
        "target_type":'targetType',
        "tier_settings":'tierSettings',
        "usage_type":'usageType'
    }

    def __init__(self,
                 archival_task_id=None,
                 ownership_context=None,
                 target_id=None,
                 target_name=None,
                 target_type=None,
                 tier_settings=None,
                 usage_type=None):
        """Constructor for the ArchivalTarget class"""

        # Initialize members of the class
        self.archival_task_id = archival_task_id
        self.ownership_context = ownership_context
        self.target_id = target_id
        self.target_name = target_name
        self.target_type = target_type
        self.tier_settings = tier_settings
        self.usage_type = usage_type


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
        archival_task_id = dictionary.get('archivalTaskId')
        ownership_context = dictionary.get('ownershipContext')
        target_id = dictionary.get('targetId')
        target_name = dictionary.get('targetName')
        target_type = dictionary.get('targetType')
        tier_settings = cohesity_management_sdk.models_v2.archival_target_tier_info.ArchivalTargetTierInfo.from_dictionary(dictionary.get('tierSettings')) if dictionary.get('tierSettings') else None
        usage_type = dictionary.get('usageType')

        # Return an object of this model
        return cls(
                   archival_task_id,
                   ownership_context,
                   target_id,
                   target_name,
                   target_type,
                   tier_settings,
                   usage_type)