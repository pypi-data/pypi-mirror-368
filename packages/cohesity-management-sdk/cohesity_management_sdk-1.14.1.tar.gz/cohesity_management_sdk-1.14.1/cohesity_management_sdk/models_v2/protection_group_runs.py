# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_protection_group_run_response_parameters

class ProtectionGroupRuns(object):

    """Implementation of the 'ProtectionGroupRuns' model.

    Protection runs.

    Attributes:
        pagination_cookie (string): Specifies the information needed in order to support pagination.
          This will not be included for the last page of results.
        runs (list of CommonProtectionGroupRunResponseParameters): Specifies
            the list of Protection Group runs.
        total_runs (long|int): Specifies the count of total runs exist for the given set of
          filters. The number of runs in single API call are limited and this count
          can be used to estimate query filter values to get next set of remaining
          runs. Please note that this field will only be populated if startTimeUsecs
          or endTimeUsecs or both are specified in query parameters.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "pagination_cookie":'paginationCookie',
        "runs":'runs',
        "total_runs":'totalRuns'
    }

    def __init__(self,
                 pagination_cookie=None,
                 runs=None,
                 total_runs=None):
        """Constructor for the ProtectionGroupRuns class"""

        # Initialize members of the class
        self.pagination_cookie = pagination_cookie
        self.runs = runs
        self.total_runs = total_runs


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
        pagination_cookie = dictionary.get('paginationCookie')
        runs = None
        if dictionary.get("runs") is not None:
            runs = list()
            for structure in dictionary.get('runs'):
                runs.append(cohesity_management_sdk.models_v2.common_protection_group_run_response_parameters.CommonProtectionGroupRunResponseParameters.from_dictionary(structure))
        total_runs = dictionary.get('totalRuns')

        # Return an object of this model
        return cls(pagination_cookie,
                   runs,
                   total_runs)