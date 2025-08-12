# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.filtering_policy_proto
import cohesity_management_sdk.models.preservation_hold_library_protection_params

class SharepPointSiteBackupEnvParams(object):

    """Implementation of the 'SharepPointSiteBackupEnvParams' model.

    Message to capture any additional backup params for SharePoint within the
    Office365 environment.

    Attributes:
        doc_lib_filtering_policy (FilteringPolicyProto): supported exclusion:
            doclib exclusion: whole doclib is excluded from backup.
            sample: /Doclib1, /Doclib1/
            directory exclusion: specified path in doclib will be excluded
            from backup.
            sample: /Doclib1/folderA/forderB
            Doclibs can be specified by either
            a) Doclib name - eg, Documents.
            b) Drive id of doclib - b!ZMSl2JRm0UeXLHfHR1m-iuD10p0CIV9qSa6TtgM
            Regular expressions are not supported. If not specified, all the
            doclibs within sharepoint site will be protected.
        phl_params (PreservationHoldLibraryProtectionParams): Specifies the
            parameters for backing up Preservation Hold Library.
            Refer PreservationHoldLibraryProtectionParams for details.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "doc_lib_filtering_policy":'docLibFilteringPolicy',
        "phl_params": 'phlParams'
    }

    def __init__(self,
                 doc_lib_filtering_policy=None,
                 phl_params=None):
        """Constructor for the SharepPointSiteBackupEnvParams class"""

        # Initialize members of the class
        self.phl_params = phl_params
        self.doc_lib_filtering_policy = doc_lib_filtering_policy


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
        doc_lib_filtering_policy = cohesity_management_sdk.models.filtering_policy_proto.FilteringPolicyProto.from_dictionary(dictionary.get('docLibFilteringPolicy')) if dictionary.get('docLibFilteringPolicy') else None
        phl_params = cohesity_management_sdk.models.preservation_hold_library_protection_params.PreservationHoldLibraryProtectionParams.from_dictionary(dictionary.get('phlParams')) if dictionary.get('phlParams') else None

        # Return an object of this model
        return cls(doc_lib_filtering_policy,
                   phl_params)


