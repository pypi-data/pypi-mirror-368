# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_protection_run_summary
import cohesity_management_sdk.models_v2.pagination_info

class GetObjectRunResponseBody(object):

    """Implementation of the 'Get Object Run Response Body.' model.

    Specifies the response body of the get object run request.

    Attributes:
        protection_runs (list of ObjectProtectionRunSummary): Specifies the
            protection runs of the given object.
        pagination_info (PaginationInfo): Specifies information needed to
            support pagination.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_runs":'protectionRuns',
        "pagination_info":'paginationInfo'
    }

    def __init__(self,
                 protection_runs=None,
                 pagination_info=None):
        """Constructor for the GetObjectRunResponseBody class"""

        # Initialize members of the class
        self.protection_runs = protection_runs
        self.pagination_info = pagination_info


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
        protection_runs = None
        if dictionary.get("protectionRuns") is not None:
            protection_runs = list()
            for structure in dictionary.get('protectionRuns'):
                protection_runs.append(cohesity_management_sdk.models_v2.object_protection_run_summary.ObjectProtectionRunSummary.from_dictionary(structure))
        pagination_info = cohesity_management_sdk.models_v2.pagination_info.PaginationInfo.from_dictionary(dictionary.get('paginationInfo')) if dictionary.get('paginationInfo') else None

        # Return an object of this model
        return cls(protection_runs,
                   pagination_info)


