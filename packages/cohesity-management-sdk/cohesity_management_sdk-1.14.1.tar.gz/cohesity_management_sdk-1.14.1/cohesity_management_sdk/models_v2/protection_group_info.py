# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protection_group_run

class ProtectionGroupInfo(object):

    """Implementation of the 'Protection Group Info' model.

    Specifies basic information about a Protection Group.

    Attributes:
        group_id (long|int): Specifies the id of the Protection Group.
        group_name (string): Specifies the name of the Protection Group.
        is_paused (bool): Specifies if the Protection Group's run is paused.
        last_run (ProtectionGroupRun): Specifies information about the last run
            for this Protection Group.
        protection_group_id (string): Specifies the protection group id.
        mtype (Type4Enum): Specifies the type of the Protection Group such as
            View or Puppeteer. 'Puppeteer' refers to a Remote Adapter Group.
            Supported environment types such as 'View', 'SQL', 'VMware', etc.
            NOTE: 'Puppeteer' refers to Cohesity's Remote Adapter. 'VMware'
            indicates the VMware Protection Source environment. 'HyperV'
            indicates the HyperV Protection Source environment. 'SQL'
            indicates the SQL Protection Source environment. 'View' indicates
            the View Protection Source environment. 'Puppeteer' indicates the
            Cohesity's Remote Adapter. 'Physical' indicates the physical
            Protection Source environment. 'Pure' indicates the Pure Storage
            Protection Source environment. 'Nimble' indicates the Nimble
            Storage Protection Source environment. 'Azure' indicates the
            Microsoft's Azure Protection Source environment. 'Netapp'
            indicates the Netapp Protection Source environment. 'Agent'
            indicates the Agent Protection Source environment. 'GenericNas'
            indicates the Generic Network Attached Storage Protection Source
            environment. 'Acropolis' indicates the Acropolis Protection Source
            environment. 'PhsicalFiles' indicates the Physical Files
            Protection Source environment. 'Isilon' indicates the Dell EMC's
            Isilon Protection Source environment. 'GPFS' indicates IBM's GPFS
            Protection Source environment. 'KVM' indicates the KVM Protection
            Source environment. 'AWS' indicates the AWS Protection Source
            environment. 'Exchange' indicates the Exchange Protection Source
            environment. 'HyperVVSS' indicates the HyperV VSS Protection
            Source environment. 'Oracle' indicates the Oracle Protection
            Source environment. 'GCP' indicates the Google Cloud Platform
            Protection Source environment. 'FlashBlade' indicates the Flash
            Blade Protection Source environment. 'AWSNative' indicates the AWS
            Native Protection Source environment. 'O365' indicates the Office
            365 Protection Source environment. 'O365Outlook' indicates Office
            365 outlook Protection Source environment. 'HyperFlex' indicates
            the Hyper Flex Protection Source environment. 'GCPNative'
            indicates the GCP Native Protection Source environment.
            'AzureNative' indicates the Azure Native Protection Source
            environment. 'Kubernetes' indicates a Kubernetes Protection Source
            environment. 'Elastifile' indicates Elastifile Protection Source
            environment. 'AD' indicates Active Directory Protection Source
            environment.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "group_id":'groupId',
        "group_name":'groupName',
        "is_paused":'isPaused',
        "last_run":'lastRun',
        "protection_group_id":'protectionGroupId',
        "mtype":'type'
    }

    def __init__(self,
                 group_id=None,
                 group_name=None,
                 is_paused=None,
                 last_run=None,
                 protection_group_id=None,
                 mtype=None):
        """Constructor for the ProtectionGroupInfo class"""

        # Initialize members of the class
        self.group_id = group_id
        self.group_name = group_name
        self.is_paused = is_paused
        self.last_run = last_run
        self.protection_group_id = protection_group_id
        self.mtype = mtype


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
        group_id = dictionary.get('groupId')
        group_name = dictionary.get('groupName')
        is_paused = dictionary.get('isPaused')
        last_run =cohesity_management_sdk.models_v2.protection_group_run.ProtectionGroupRun.from_dictionary(dictionary.get('lastRun')) if dictionary.get('lastRun') else None
        protection_group_id = dictionary.get('protectionGroupId')
        mtype = dictionary.get('type')

        # Return an object of this model
        return cls(group_id,
                   group_name,
                   is_paused,
                   last_run,
                   protection_group_id,
                   mtype)