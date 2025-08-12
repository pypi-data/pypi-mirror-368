# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.cloud_spin_result_for_a_target

class SummaryInformationForCloudSpinRun(object):

    """Implementation of the 'Summary information for cloud spin run.' model.

    Specifies summary information about cloud spin run.

    Attributes:
        cloud_spin_target_results (list of CloudSpinResultForATarget): Cloud
            Spin results for each Cloud Spin target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cloud_spin_target_results":'cloudSpinTargetResults'
    }

    def __init__(self,
                 cloud_spin_target_results=None):
        """Constructor for the SummaryInformationForCloudSpinRun class"""

        # Initialize members of the class
        self.cloud_spin_target_results = cloud_spin_target_results


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
        cloud_spin_target_results = None
        if dictionary.get("cloudSpinTargetResults") is not None:
            cloud_spin_target_results = list()
            for structure in dictionary.get('cloudSpinTargetResults'):
                cloud_spin_target_results.append(cohesity_management_sdk.models_v2.cloud_spin_result_for_a_target.CloudSpinResultForATarget.from_dictionary(structure))

        # Return an object of this model
        return cls(cloud_spin_target_results)


