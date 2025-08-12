# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protection_run_summary

class ProtectionRunsSummary(object):

    """Implementation of the 'ProtectionRunsSummary' model.

    Specifies a list of summaries of protection runs.

    Attributes:
        protection_runs_summary (list of ProtectionRunSummary): Specifies a
            list of summaries of protection runs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_runs_summary":'protectionRunsSummary'
    }

    def __init__(self,
                 protection_runs_summary=None):
        """Constructor for the ProtectionRunsSummary class"""

        # Initialize members of the class
        self.protection_runs_summary = protection_runs_summary


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
        protection_runs_summary = None
        if dictionary.get("protectionRunsSummary") is not None:
            protection_runs_summary = list()
            for structure in dictionary.get('protectionRunsSummary'):
                protection_runs_summary.append(cohesity_management_sdk.models_v2.protection_run_summary.ProtectionRunSummary.from_dictionary(structure))

        # Return an object of this model
        return cls(protection_runs_summary)


