# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.office_365_protection_group_object_params
import cohesity_management_sdk.models_v2.office_365_one_drive_protection_group_parameters
import cohesity_management_sdk.models_v2.office_365_o_365_outlook_protection_group_parameters
import cohesity_management_sdk.models_v2.office_365_o_365_public_folders_protection_group_parameters
import cohesity_management_sdk.models_v2.office_365_sharepoint_protection_group_parameters

class Office365ProtectionGroupParams(object):
    """Implementation of the 'Office365ProtectionGroupParams' model.

    Specifies the parameters which are specific to Office 365 related Protection Groups.

    Attributes:
        exclude_object_ids (list of long||int): Specifies the objects to be excluded in the Protection Group.
        indexing_policy (IndexingPolicy): Specifies the fields required to enable indexing of the protected objects such as files and directories.
        objects (list of Office365ProtectionGroupObjectParams): Specifies the objects to be included in the Protection Group.
        one_drive_protection_type_params (Office365OneDriveProtectionGroupParameters): Specifies the parameters specific to OneDrive Protection Group type.
        outlook_protection_type_params (Office365O365OutlookProtectionGroupParameters): Specifies the parameters specific to Outlook Protection Group type.
        protection_types (ProtectionType9Enum): Specifies the Office 365 Protection Group types.
        public_folders_protection_type_params (Office365O365PublicFoldersProtectionGroupParameters): Specifies the parameters specific to PublicFolders Protection Group type.
        share_point_protection_type_params (Office365SharepointProtectionGroupParameters): Specifies the parameters specific to SharePoint Protection Group type.
        source_id (int): Specifies the id of the parent of the objects.
        source_name (str): Specifies the name of the parent of the objects.
    """

    _names = {
        "exclude_object_ids":"excludeObjectIds",
        "indexing_policy":"indexingPolicy",
        "objects":"objects",
        "one_drive_protection_type_params":"oneDriveProtectionTypeParams",
        "outlook_protection_type_params":"outlookProtectionTypeParams",
        "protection_types":"protectionTypes",
        "public_folders_protection_type_params":"publicFoldersProtectionTypeParams",
        "share_point_protection_type_params":"sharePointProtectionTypeParams",
        "source_id":"sourceId",
        "source_name":"sourceName",
    }

    def __init__(self,
                 exclude_object_ids=None,
                 indexing_policy=None,
                 objects=None,
                 one_drive_protection_type_params=None,
                 outlook_protection_type_params=None,
                 protection_types=None,
                 public_folders_protection_type_params=None,
                 share_point_protection_type_params=None,
                 source_id=None,
                 source_name=None):
        """Constructor for the Office365ProtectionGroupParams class"""

        self.exclude_object_ids = exclude_object_ids
        self.indexing_policy = indexing_policy
        self.objects = objects
        self.one_drive_protection_type_params = one_drive_protection_type_params
        self.outlook_protection_type_params = outlook_protection_type_params
        self.protection_types = protection_types
        self.public_folders_protection_type_params = public_folders_protection_type_params
        self.share_point_protection_type_params = share_point_protection_type_params
        self.source_id = source_id
        self.source_name = source_name


    @classmethod
    def from_dictionary(cls, dictionary):
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

        exclude_object_ids = dictionary.get('excludeObjectIds')
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        objects = None
        if dictionary.get('objects') is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.office_365_protection_group_object_params.Office365ProtectionGroupObjectParams.from_dictionary(structure))
        one_drive_protection_type_params = cohesity_management_sdk.models_v2.office_365_one_drive_protection_group_parameters.Office365OneDriveProtectionGroupParameters.from_dictionary(dictionary.get('oneDriveProtectionTypeParams')) if dictionary.get('oneDriveProtectionTypeParams') else None
        outlook_protection_type_params = cohesity_management_sdk.models_v2.office_365_o_365_outlook_protection_group_parameters.Office365O365OutlookProtectionGroupParameters.from_dictionary(dictionary.get('outlookProtectionTypeParams')) if dictionary.get('outlookProtectionTypeParams') else None
        protection_types = dictionary.get('protectionTypes')
        public_folders_protection_type_params = cohesity_management_sdk.models_v2.office_365_o_365_public_folders_protection_group_parameters.Office365O365PublicFoldersProtectionGroupParameters.from_dictionary(dictionary.get('publicFoldersProtectionTypeParams')) if dictionary.get('publicFoldersProtectionTypeParams') else None
        share_point_protection_type_params = cohesity_management_sdk.models_v2.office_365_sharepoint_protection_group_parameters.Office365SharepointProtectionGroupParameters.from_dictionary(dictionary.get('sharePointProtectionTypeParams')) if dictionary.get('sharePointProtectionTypeParams') else None
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')

        return cls(
            exclude_object_ids,
            indexing_policy,
            objects,
            one_drive_protection_type_params,
            outlook_protection_type_params,
            protection_types,
            public_folders_protection_type_params,
            share_point_protection_type_params,
            source_id,
            source_name
        )