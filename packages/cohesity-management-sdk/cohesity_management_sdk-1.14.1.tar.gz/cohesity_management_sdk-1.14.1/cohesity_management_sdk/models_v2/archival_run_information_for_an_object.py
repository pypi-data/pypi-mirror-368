# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.archival_result_for_a_target

class ArchivalRunInformationForAnObject(object):

    """Implementation of the 'Archival run information for an object.' model.

    Specifies information about archival run for an object.

    Attributes:
        archival_target_results (list of ArchivalResultForATarget): Archival
            result for an archival target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "archival_target_results":'archivalTargetResults'
    }

    def __init__(self,
                 archival_target_results=None):
        """Constructor for the ArchivalRunInformationForAnObject class"""

        # Initialize members of the class
        self.archival_target_results = archival_target_results


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
        archival_target_results = None
        if dictionary.get("archivalTargetResults") is not None:
            archival_target_results = list()
            for structure in dictionary.get('archivalTargetResults'):
                archival_target_results.append(cohesity_management_sdk.models_v2.archival_result_for_a_target.ArchivalResultForATarget.from_dictionary(structure))

        # Return an object of this model
        return cls(archival_target_results)


