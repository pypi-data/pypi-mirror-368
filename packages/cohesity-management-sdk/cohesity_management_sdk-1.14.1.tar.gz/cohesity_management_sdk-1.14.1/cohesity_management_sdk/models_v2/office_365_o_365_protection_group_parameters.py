# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.office_365_protection_group_object_params
import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.office_365_o_365_outlook_protection_group_parameters
import cohesity_management_sdk.models_v2.office_365_one_drive_protection_group_parameters
import cohesity_management_sdk.models_v2.office_365_o_365_public_folders_protection_group_parameters
import cohesity_management_sdk.models_v2.office_365_sharepoint_protection_group_parameters

class Office365O365ProtectionGroupParameters(object):

    """Implementation of the 'Office 365(o365) Protection Group Parameters.' model.

    Specifies the parameters which are specific to Office 365 related
    Protection Groups.

    Attributes:
        objects (list of Office365ProtectionGroupObjectParams): Specifies the
            objects to be included in the Protection Group.
        exclude_object_ids (list of long|int): Specifies the objects to be
            excluded in the Protection Group.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        protection_types (list of ProtectionType9Enum): Specifies the Office
            365 Protection Group types.
        outlook_protection_type_params
            (Office365O365OutlookProtectionGroupParameters): Specifies the
            parameters which are specific to Office 365 Outlook related
            Protection Groups.
        one_drive_protection_type_params
            (Office365OneDriveProtectionGroupParameters): Specifies the
            parameters which are specific to Office 365 OneDrive related
            Protection Groups.
        public_folders_protection_type_params
            (Office365O365PublicFoldersProtectionGroupParameters): Specifies
            the parameters which are specific to Office 365 PublicFolders
            related Protection Groups.
        share_point_protection_type_params (Office365SharePointProtectionGroupParams):
            Specifies the parameters specific to SharePoint Protection Group
          type.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "protection_types":'protectionTypes',
        "exclude_object_ids":'excludeObjectIds',
        "indexing_policy":'indexingPolicy',
        "outlook_protection_type_params":'outlookProtectionTypeParams',
        "one_drive_protection_type_params":'oneDriveProtectionTypeParams',
        "public_folders_protection_type_params":'publicFoldersProtectionTypeParams',
        "share_point_protection_type_params":'sharePointProtectionTypeParams',
        "source_id":'sourceId',
        "source_name":'sourceName'
    }

    def __init__(self,
                 objects=None,
                 protection_types=None,
                 exclude_object_ids=None,
                 indexing_policy=None,
                 outlook_protection_type_params=None,
                 one_drive_protection_type_params=None,
                 public_folders_protection_type_params=None,
                 share_point_protection_type_params=None,
                 source_id=None,
                 source_name=None):
        """Constructor for the Office365O365ProtectionGroupParameters class"""

        # Initialize members of the class
        self.objects = objects
        self.exclude_object_ids = exclude_object_ids
        self.indexing_policy = indexing_policy
        self.protection_types = protection_types
        self.outlook_protection_type_params = outlook_protection_type_params
        self.one_drive_protection_type_params = one_drive_protection_type_params
        self.public_folders_protection_type_params = public_folders_protection_type_params
        self.share_point_protection_type_params = share_point_protection_type_params
        self.source_id = source_id
        self.source_name = source_name


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
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.office_365_protection_group_object_params.Office365ProtectionGroupObjectParams.from_dictionary(structure))
        protection_types = dictionary.get('protectionTypes')
        exclude_object_ids = dictionary.get('excludeObjectIds')
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        outlook_protection_type_params = cohesity_management_sdk.models_v2.office_365_o_365_outlook_protection_group_parameters.Office365O365OutlookProtectionGroupParameters.from_dictionary(dictionary.get('outlookProtectionTypeParams')) if dictionary.get('outlookProtectionTypeParams') else None
        one_drive_protection_type_params = cohesity_management_sdk.models_v2.office_365_one_drive_protection_group_parameters.Office365OneDriveProtectionGroupParameters.from_dictionary(dictionary.get('oneDriveProtectionTypeParams')) if dictionary.get('oneDriveProtectionTypeParams') else None
        public_folders_protection_type_params = cohesity_management_sdk.models_v2.office_365_o_365_public_folders_protection_group_parameters.Office365O365PublicFoldersProtectionGroupParameters.from_dictionary(dictionary.get('publicFoldersProtectionTypeParams')) if dictionary.get('publicFoldersProtectionTypeParams') else None
        share_point_protection_type_params = cohesity_management_sdk.models_v2.office_365_sharepoint_protection_group_parameters.Office365SharepointProtectionGroupParameters.from_dictionary(dictionary.get('sharePointProtectionTypeParams')) if dictionary.get('sharePointProtectionTypeParams') else None
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')

        # Return an object of this model
        return cls(objects,
                   protection_types,
                   exclude_object_ids,
                   indexing_policy,
                   outlook_protection_type_params,
                   one_drive_protection_type_params,
                   public_folders_protection_type_params,
                   share_point_protection_type_params,
                   source_id,
                   source_name)