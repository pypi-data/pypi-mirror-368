# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protection_runs_stats

class ProtectionRunsStatsList(object):

    """Implementation of the 'ProtectionRunsStatsList' model.

    Specifies the statistics of protection runs at the specific time.

    Attributes:
        timestamp (long|int): Specifies a Unix epoch Timestamp (in
            microseconds) of this statistics.
        stats (list of ProtectionRunsStats): Specifies the protection runs
            stats.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "timestamp":'timestamp',
        "stats":'stats'
    }

    def __init__(self,
                 timestamp=None,
                 stats=None):
        """Constructor for the ProtectionRunsStatsList class"""

        # Initialize members of the class
        self.timestamp = timestamp
        self.stats = stats


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
        timestamp = dictionary.get('timestamp')
        stats = None
        if dictionary.get("stats") is not None:
            stats = list()
            for structure in dictionary.get('stats'):
                stats.append(cohesity_management_sdk.models_v2.protection_runs_stats.ProtectionRunsStats.from_dictionary(structure))

        # Return an object of this model
        return cls(timestamp,
                   stats)


