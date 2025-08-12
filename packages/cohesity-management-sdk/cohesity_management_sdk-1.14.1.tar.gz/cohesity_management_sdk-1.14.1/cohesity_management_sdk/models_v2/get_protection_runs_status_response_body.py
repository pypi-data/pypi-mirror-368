# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protection_runs_stats_list

class GetProtectionRunsStatusResponseBody(object):

    """Implementation of the 'GetProtectionRunsStatusResponseBody' model.

    Specifies a list of protection runs stats taken at different time.

    Attributes:
        protection_runs_stats_list (list of ProtectionRunsStatsList):
            Specifies a list of protection runs stats taken at different
            time.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_runs_stats_list":'protectionRunsStatsList'
    }

    def __init__(self,
                 protection_runs_stats_list=None):
        """Constructor for the GetProtectionRunsStatusResponseBody class"""

        # Initialize members of the class
        self.protection_runs_stats_list = protection_runs_stats_list


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
        protection_runs_stats_list = None
        if dictionary.get("protectionRunsStatsList") is not None:
            protection_runs_stats_list = list()
            for structure in dictionary.get('protectionRunsStatsList'):
                protection_runs_stats_list.append(cohesity_management_sdk.models_v2.protection_runs_stats_list.ProtectionRunsStatsList.from_dictionary(structure))

        # Return an object of this model
        return cls(protection_runs_stats_list)


