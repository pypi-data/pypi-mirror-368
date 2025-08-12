# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.failed_run_details

class UpdateProtectionGroupRunResponseBody(object):

    """Implementation of the 'Update Protection Group Run Response Body.' model.

    Specifies the response of update Protection Group Runs request.

    Attributes:
        successful_run_ids (list of string): Specifies a list of ids of
            Protection Group Runs that are successfully updated.
        failed_runs (list of FailedRunDetails): Specifies a list of ids of
            Protection Group Runs that failed to update along with error
            details.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "successful_run_ids":'successfulRunIds',
        "failed_runs":'failedRuns'
    }

    def __init__(self,
                 successful_run_ids=None,
                 failed_runs=None):
        """Constructor for the UpdateProtectionGroupRunResponseBody class"""

        # Initialize members of the class
        self.successful_run_ids = successful_run_ids
        self.failed_runs = failed_runs


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
        successful_run_ids = dictionary.get('successfulRunIds')
        failed_runs = None
        if dictionary.get("failedRuns") is not None:
            failed_runs = list()
            for structure in dictionary.get('failedRuns'):
                failed_runs.append(cohesity_management_sdk.models_v2.failed_run_details.FailedRunDetails.from_dictionary(structure))

        # Return an object of this model
        return cls(successful_run_ids,
                   failed_runs)


