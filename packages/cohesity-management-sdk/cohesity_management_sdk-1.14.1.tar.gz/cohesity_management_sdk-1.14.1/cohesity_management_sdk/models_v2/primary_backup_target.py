# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.primary_archival_target

class PrimaryBackupTarget(object):

    """Implementation of the 'PrimaryBackupTarget' model.

    Specifies the primary backup target settings for regular backups. If the
    backup target field is not specified then backup will be taken locally on
    the Cohesity cluster.

    Attributes:
        target_type (TargetType5Enum): Specifies the primary backup location
            where backups will be stored. If not specified, then default is
            assumed as local backup on Cohesity cluster.
        archival_target_settings (PrimaryArchivalTarget): Specifies the
            primary archival settings. Mainly used for cloud direct archive
            (CAD) policy where primary backup is stored on archival target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_type":'targetType',
        "archival_target_settings":'archivalTargetSettings'
    }

    def __init__(self,
                 target_type='Local',
                 archival_target_settings=None):
        """Constructor for the PrimaryBackupTarget class"""

        # Initialize members of the class
        self.target_type = target_type
        self.archival_target_settings = archival_target_settings


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
        target_type = dictionary.get("targetType") if dictionary.get("targetType") else 'Local'
        archival_target_settings = cohesity_management_sdk.models_v2.primary_archival_target.PrimaryArchivalTarget.from_dictionary(dictionary.get('archivalTargetSettings')) if dictionary.get('archivalTargetSettings') else None

        # Return an object of this model
        return cls(target_type,
                   archival_target_settings)