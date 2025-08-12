# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.aws_tiers
import cohesity_management_sdk.models_v2.azure_tiers
import cohesity_management_sdk.models_v2.google_tiers
import cohesity_management_sdk.models_v2.oracle_tiers

class ArchivalTargetTierInfo(object):

    """Implementation of the 'Archival Target Tier Info' model.

    Specifies the tier info for archival.

    Attributes:
        cloud_platform (CloudPlatformEnum): Specifies the cloud platform to
            enable tiering.
        aws_tiering (AWSTiers): Specifies aws tiers.
        azure_tiering (AzureTiers): Specifies Azure tiers.
        google_tiering (GoogleTiers): Specifies Google tiers.
        oracle_tiering (OracleTiers): Specifies Oracle tiers.
        current_tier_type (CurrentTierTypeEnum): Specifies the type of the
            current tier where the snapshot resides. This will be specified if
            the run is a CAD run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cloud_platform":'cloudPlatform',
        "aws_tiering":'awsTiering',
        "azure_tiering":'azureTiering',
        "google_tiering":'googleTiering',
        "oracle_tiering":'oracleTiering',
        "current_tier_type":'currentTierType'
    }

    def __init__(self,
                 cloud_platform=None,
                 aws_tiering=None,
                 azure_tiering=None,
                 google_tiering=None,
                 oracle_tiering=None,
                 current_tier_type=None):
        """Constructor for the ArchivalTargetTierInfo class"""

        # Initialize members of the class
        self.cloud_platform = cloud_platform
        self.aws_tiering = aws_tiering
        self.azure_tiering = azure_tiering
        self.google_tiering = google_tiering
        self.oracle_tiering = oracle_tiering
        self.current_tier_type = current_tier_type


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
        current_tier_type = dictionary.get('currentTierType')

        # Return an object of this model
        return cls(cloud_platform,
                   aws_tiering,
                   azure_tiering,
                   google_tiering,
                   oracle_tiering,
                   current_tier_type)


