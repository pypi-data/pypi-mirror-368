# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.filtering_policy_proto
import cohesity_management_sdk.models.preservation_hold_library_protection_params
import cohesity_management_sdk.models.attribute_filter_policy

class OneDriveBackupEnvParams(object):

    """Implementation of the 'OneDriveBackupEnvParams' model.

    Message to capture any additonal backup params for OneDrive within the
    Office365 environment.

    Attributes:
        attr_filter_policy (AttributeFilterPolicy): Specifies attribute filter
            policy to support inclusion/exclusions of entities
        filtering_policy (FilteringPolicyProto): Proto to encapsulate the
            filtering policy for backup objects like files or directories. If
            an object is not matched by any of the 'allow_filters', it will be
            excluded in the backup. If an object is matched by one of the
            'deny_filters', it will always be excluded in the backup.
            Basically 'deny_filters' overwrite 'allow_filters' if they both
            match the same object. Currently we only support two kinds of
            filter: prefix which always starts with '/', or postfix which
            always starts with '*' (cannot be "*" only). We don't support
            regular expression right now. A concrete example is: Allow
            filters: "/" Deny filters: "/tmp", "*.mp4" Using such a policy
            will include everything under the root directory except the /tmp
            directory and all the mp4 files.
        phl_params (PreservationHoldLibraryProtectionParams): Specifies the parameters for backing up Preservation Hold Library.
          Refer PreservationHoldLibraryProtectionParams for details.
        should_backup_onedrive (bool): Specifies whether the OneDrive(s) for
            all the Office365 Users present in the protection job should be
            backed up.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "attr_filter_policy": 'attrFilterPolicy',
        "filtering_policy":'filteringPolicy',
        "phl_params":'phlParams',
        "should_backup_onedrive":'shouldBackupOnedrive'
    }

    def __init__(self,
                 attr_filter_policy=None,
                 filtering_policy=None,
                 phl_params=None,
                 should_backup_onedrive=None):
        """Constructor for the OneDriveBackupEnvParams class"""

        # Initialize members of the class
        self.attr_filter_policy = attr_filter_policy
        self.filtering_policy = filtering_policy
        self.phl_params = phl_params
        self.should_backup_onedrive = should_backup_onedrive


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
        attr_filter_policy = cohesity_management_sdk.models.attribute_filter_policy.AttributeFilterPolicy.from_dictionary(dictionary.get('attrFilterPolicy')) if dictionary.get('attrFilterPolicy') else None
        filtering_policy = cohesity_management_sdk.models.filtering_policy_proto.FilteringPolicyProto.from_dictionary(dictionary.get('filteringPolicy')) if dictionary.get('filteringPolicy') else None
        phl_params = cohesity_management_sdk.models.preservation_hold_library_protection_params.PreservationHoldLibraryProtectionParams.from_dictionary(dictionary.get('phlParams'))
        should_backup_onedrive = dictionary.get('shouldBackupOnedrive')

        # Return an object of this model
        return cls(attr_filter_policy,
                   filtering_policy,
                   phl_params,
                   should_backup_onedrive)