# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.classification_info
import cohesity_management_sdk.models.data_insights_info
import cohesity_management_sdk.models.data_governance_info
import cohesity_management_sdk.models.data_protect_info
import cohesity_management_sdk.models.data_protect_azure_info
import cohesity_management_sdk.models.fort_knox_azure_info
import cohesity_management_sdk.models.fort_knox_cold_info
import cohesity_management_sdk.models.ransomware_info
import cohesity_management_sdk.models.site_continuity_info
import cohesity_management_sdk.models.threat_protection_info


class SubscriptionInfo(object):

    """Implementation of the 'SubscriptionInfo' model.

    Extends this to have Helios, DRaaS and DSaaS.


    Attributes:
        classification (ClassificationInfo): Specifies whether Datahawk
            Classification subscription was/is enabled for account.
        data_insights (DataInsightsInfo): Specifies whether Data Insights
            subscription was/is enabled for account.
        data_governance (DataGovernanceInfo): Specifies whether data governance
            subscription was/is enabled for account.
        data_protect (DataProtectInfo): Specifies whether data protect
            subscription was subscribed for account.
        data_protect_azure (DataProtectAzureInfo): Specifies whether data
            protect subscription was subscribed for account.
            This is for Azure data plane.
        fort_knox_azure_cool (FortKnoxAzureInfo): Specifies whether Fortknox
            AzureCool or AzureCool FreeTrial subscription was/is enabled for
            account.
        fort_knox_azure_hot (FortKnoxAzureInfo): Specifies whether Fortknox
            AzureHot or AzureHot FreeTrial subscription was/is enabled for
            account.
        fort_knox_cold (FortKnoxColdInfo): Specifies whether Fortknox AwsCold
            or AwsCold FreeTrial subscription was/is enabled for account.
        ransomware (RansomwareInfo): Specifies whether ransomware subscription
            was/is enabled for account.
        site_continuity (SiteContinuityInfo): Specifies whether site continuity
            subscription was/is enabled for account.
        threat_protection (ThreatProtectionInfo): Specifies whether Datahawk
            ThreatProtection subscription was/is enabled for account.
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "classification": 'classification',
        "data_insights": 'dataInsights',
        "data_governance":'dataGovernance',
        "data_protect":'dataProtect',
        "data_protect_azure": 'dataProtectAzure',
        "fort_knox_azure_cool": 'fortKnoxAzureCool',
        "fort_knox_azure_hot": 'fortKnoxAzureHot',
        "fort_knox_cold": 'fortKnoxCold',
        "ransomware":'ransomware',
        "site_continuity":'siteContinuity',
        "threat_protection": 'threatProtection'
    }
    def __init__(self,
                 classification=None,
                 data_insights=None,
                 data_governance=None,
                 data_protect=None,
                 data_protect_azure=None,
                 fort_knox_azure_cool=None,
                 fort_knox_azure_hot=None,
                 fort_knox_cold=None,
                 ransomware=None,
                 site_continuity=None,
                 threat_protection=None
            ):

        """Constructor for the SubscriptionInfo class"""

        # Initialize members of the class
        self.classification = classification
        self.data_insights = data_insights
        self.data_governance = data_governance
        self.data_protect = data_protect
        self.data_protect_azure = data_protect_azure
        self.fort_knox_azure_cool = fort_knox_azure_cool
        self.fort_knox_azure_hot = fort_knox_azure_hot
        self.fort_knox_cold = fort_knox_cold
        self.ransomware = ransomware
        self.site_continuity = site_continuity
        self.threat_protection = threat_protection

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
        classification = cohesity_management_sdk.models.classification_info.ClassificationInfo.from_dictionary(dictionary.get('classification')) if dictionary.get('classification') else None
        data_insights = cohesity_management_sdk.models.data_insights_info.DataInsightsInfo.from_dictionary(dictionary.get('dataInsights')) if dictionary.get('dataInsights') else None
        data_governance = cohesity_management_sdk.models.data_governance_info.DataGovernanceInfo.from_dictionary(dictionary.get('dataGovernance')) if dictionary.get('dataGovernance') else None
        data_protect = cohesity_management_sdk.models.data_protect_info.DataProtectInfo.from_dictionary(dictionary.get('dataProtect')) if dictionary.get('dataProtect') else None
        data_protect_azure = cohesity_management_sdk.models.data_protect_azure_info.DataProtectAzureInfo.from_dictionary(dictionary.get('dataProtectAzure')) if dictionary.get('dataProtectAzure') else None
        fort_knox_azure_cool = cohesity_management_sdk.models.fort_knox_azure_info.FortKnoxAzureInfo.from_dictionary(dictionary.get('fortKnoxAzureCool')) if dictionary.get('fortKnoxAzureCool') else None
        fort_knox_azure_hot = cohesity_management_sdk.models.fort_knox_azure_info.FortKnoxAzureInfo.from_dictionary(dictionary.get('fortKnoxAzureHot')) if dictionary.get('fortKnoxAzureHot') else None
        fort_knox_cold = cohesity_management_sdk.models.fort_knox_cold_info.FortKnoxColdInfo.from_dictionary(dictionary.get('fortKnoxCold')) if dictionary.get('fortKnoxCold') else None
        ransomware = cohesity_management_sdk.models.ransomware_info.RansomwareInfo.from_dictionary(dictionary.get('ransomware')) if dictionary.get('ransomware') else None
        site_continuity = cohesity_management_sdk.models.site_continuity_info.SiteContinuityInfo.from_dictionary(dictionary.get('siteContinuity')) if dictionary.get('siteContinuity') else None
        threat_protection = cohesity_management_sdk.models.threat_protection_info.ThreatProtectionInfo.from_dictionary(dictionary.get('threatProtection')) if dictionary.get('threatProtection') else None

        # Return an object of this model
        return cls(
            classification,
            data_insights,
            data_governance,
            data_protect,
            data_protect_azure,
            fort_knox_azure_cool,
            fort_knox_azure_hot,
            fort_knox_cold,
            ransomware,
            site_continuity,
            threat_protection
)