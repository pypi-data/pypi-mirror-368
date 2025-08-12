# -*- coding: utf-8 -*-


class ProtectionRunsStats(object):

    """Implementation of the 'ProtectionRunsStats' model.

    Specifies the statistics of protection runs.

    Attributes:
        protection_run_status (ProtectionRunStatusEnum): Specifies the status
            of protection runs.
        protection_runs_count (long|int): Specifies the number of protection
            runs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_run_status":'protectionRunStatus',
        "protection_runs_count":'protectionRunsCount'
    }

    def __init__(self,
                 protection_run_status=None,
                 protection_runs_count=None):
        """Constructor for the ProtectionRunsStats class"""

        # Initialize members of the class
        self.protection_run_status = protection_run_status
        self.protection_runs_count = protection_runs_count


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
        protection_run_status = dictionary.get('protectionRunStatus')
        protection_runs_count = dictionary.get('protectionRunsCount')

        # Return an object of this model
        return cls(protection_run_status,
                   protection_runs_count)


