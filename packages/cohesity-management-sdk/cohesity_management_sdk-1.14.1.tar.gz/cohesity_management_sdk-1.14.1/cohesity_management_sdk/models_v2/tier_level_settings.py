# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.aws_tiers
import cohesity_management_sdk.models_v2.azure_tiers
import cohesity_management_sdk.models_v2.google_tiers
import cohesity_management_sdk.models_v2.oracle_tiers

class TierLevelSettings(object):

    """Implementation of the 'TierLevelSettings' model.

    Specifies the settings tier levels configured with each archival target.
    The tier settings need to be applied in specific order and default tier
    should always be passed as first entry in tiers array. The following
    example illustrates how to configure tiering input for AWS tiering. Same
    type of input structure applied to other cloud platforms also. <br>If user
    wants to achieve following tiering for backup, <br>User Desired Tiering-
    <br><t>1.Archive Full back up for 12 Months <br><t>2.Tier Levels
    <br><t><t>[1,12] [ <br><t><t><t>s3 (1 to 2 months), (default tier)
    <br><t><t><t>s3 Intelligent tiering (3 to 6 months), <br><t><t><t>s3 One
    Zone (7 to 9 months) <br><t><t><t>Glacier (10 to 12 months)] <br><t>API
    Input <br><t><t>1.tiers-[ <br><t><t><t>{'tierType':
    'S3','moveAfterUnit':'months', <br><t><t><t>'moveAfter':2 - move from s3
    to s3Inte after 2 months}, <br><t><t><t>{'tierType':
    'S3Inte','moveAfterUnit':'months', <br><t><t><t>'moveAfter':4 - move from
    S3Inte to Glacier after 4 months}, <br><t><t><t>{'tierType': 'Glacier',
    'moveAfterUnit':'months', <br><t><t><t>'moveAfter': 3 - move from Glacier
    to S3 One Zone after 3 months }, <br><t><t><t>{'tierType': 'S3 One Zone',
    'moveAfterUnit': nil, <br><t><t><t>'moveAfter': nil - For the last record,
    'moveAfter' and 'moveAfterUnit' <br><t><t><t>will be ignored since there
    are no further tier for data movement } <br><t><t><t>}]

    Attributes:
        aws_tiering (AWSTiers): Specifies aws tiers.
        azure_tiering (AzureTiers): Specifies Azure tiers.
        cloud_platform (CloudPlatformEnum): Specifies the cloud platform to
            enable tiering.
        google_tiering (GoogleTiers): Specifies Google tiers.
        oracle_tiering (OracleTiers): Specifies Oracle tiers.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cloud_platform":'cloudPlatform',
        "aws_tiering":'awsTiering',
        "azure_tiering":'azureTiering',
        "google_tiering":'googleTiering',
        "oracle_tiering":'oracleTiering'
    }

    def __init__(self,
                 cloud_platform=None,
                 aws_tiering=None,
                 azure_tiering=None,
                 google_tiering=None,
                 oracle_tiering=None):
        """Constructor for the TierLevelSettings class"""

        # Initialize members of the class
        self.cloud_platform = cloud_platform
        self.aws_tiering = aws_tiering
        self.azure_tiering = azure_tiering
        self.google_tiering = google_tiering
        self.oracle_tiering = oracle_tiering


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
        cloud_platform = dictionary.get('cloudPlatform')
        aws_tiering = cohesity_management_sdk.models_v2.aws_tiers.AWSTiers.from_dictionary(dictionary.get('awsTiering')) if dictionary.get('awsTiering') else None
        azure_tiering = cohesity_management_sdk.models_v2.azure_tiers.AzureTiers.from_dictionary(dictionary.get('azureTiering')) if dictionary.get('azureTiering') else None
        google_tiering = cohesity_management_sdk.models_v2.google_tiers.GoogleTiers.from_dictionary(dictionary.get('googleTiering')) if dictionary.get('googleTiering') else None
        oracle_tiering = cohesity_management_sdk.models_v2.oracle_tiers.OracleTiers.from_dictionary(dictionary.get('oracleTiering')) if dictionary.get('oracleTiering') else None

        # Return an object of this model
        return cls(cloud_platform,
                   aws_tiering,
                   azure_tiering,
                   google_tiering,
                   oracle_tiering)