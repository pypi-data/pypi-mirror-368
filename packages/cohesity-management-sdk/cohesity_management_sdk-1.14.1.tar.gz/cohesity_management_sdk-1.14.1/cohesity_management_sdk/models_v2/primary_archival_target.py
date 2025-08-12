# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.tier_level_settings

class PrimaryArchivalTarget(object):

    """Implementation of the 'PrimaryArchivalTarget' model.

    Specifies the primary archival settings. Mainly used for cloud direct
    archive (CAD) policy where primary backup is stored on archival target.

    Attributes:
        target_id (long|int): Specifies the Archival target id to take primary
            backup.
        target_name (string): Specifies the Archival target name where
            Snapshots are copied.
        tier_settings (TierLevelSettings): Specifies the settings tier levels
            configured with each archival target. The tier settings need to be
            applied in specific order and default tier should always be passed
            as first entry in tiers array. The following example illustrates
            how to configure tiering input for AWS tiering. Same type of input
            structure applied to other cloud platforms also. <br>If user wants
            to achieve following tiering for backup, <br>User Desired Tiering-
            <br><t>1.Archive Full back up for 12 Months <br><t>2.Tier Levels
            <br><t><t>[1,12] [ <br><t><t><t>s3 (1 to 2 months), (default tier)
            <br><t><t><t>s3 Intelligent tiering (3 to 6 months),
            <br><t><t><t>s3 One Zone (7 to 9 months) <br><t><t><t>Glacier (10
            to 12 months)] <br><t>API Input <br><t><t>1.tiers-[
            <br><t><t><t>{'tierType': 'S3','moveAfterUnit':'months',
            <br><t><t><t>'moveAfter':2 - move from s3 to s3Inte after 2
            months}, <br><t><t><t>{'tierType':
            'S3Inte','moveAfterUnit':'months', <br><t><t><t>'moveAfter':4 -
            move from S3Inte to Glacier after 4 months},
            <br><t><t><t>{'tierType': 'Glacier', 'moveAfterUnit':'months',
            <br><t><t><t>'moveAfter': 3 - move from Glacier to S3 One Zone
            after 3 months }, <br><t><t><t>{'tierType': 'S3 One Zone',
            'moveAfterUnit': nil, <br><t><t><t>'moveAfter': nil - For the last
            record, 'moveAfter' and 'moveAfterUnit' <br><t><t><t>will be
            ignored since there are no further tier for data movement }
            <br><t><t><t>}]

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_id":'targetId',
        "target_name":'targetName',
        "tier_settings":'tierSettings'
    }

    def __init__(self,
                 target_id=None,
                 target_name=None,
                 tier_settings=None):
        """Constructor for the PrimaryArchivalTarget class"""

        # Initialize members of the class
        self.target_id = target_id
        self.target_name = target_name
        self.tier_settings = tier_settings


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
        target_id = dictionary.get('targetId')
        target_name = dictionary.get('targetName')
        tier_settings = cohesity_management_sdk.models_v2.tier_level_settings.TierLevelSettings.from_dictionary(dictionary.get('tierSettings')) if dictionary.get('tierSettings') else None

        # Return an object of this model
        return cls(target_id,
                   target_name,
                   tier_settings)


