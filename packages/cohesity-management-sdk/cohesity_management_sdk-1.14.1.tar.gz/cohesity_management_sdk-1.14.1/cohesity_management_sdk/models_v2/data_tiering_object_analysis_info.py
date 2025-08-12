# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.data_tiering_share_stats

class DataTieringObjectAnalysisInfo(object):

    """Implementation of the 'DataTieringObjectAnalysisInfo' model.

    Specifies the data tiering object analysis details.

    Attributes:
        status (Status9Enum): Status of the analysis run. 'Running' indicates
            that the run is still running. 'Canceled' indicates that the run
            has been canceled. 'Canceling' indicates that the run is in the
            process of being  canceled. 'Failed' indicates that the run has
            failed. 'Missed' indicates that the run was unable to take place
            at the  scheduled time because the previous run was still
            happening. 'Succeeded' indicates that the run has finished
            successfully. 'SucceededWithWarning' indicates that the run
            finished  successfully, but there were some warning messages.
            'OnHold' indicates that the run has On hold.
        message (string): A message about the error if encountered while
            performing data tiering analysis.
        stats (list of DataTieringShareStats): Specifies the source share
            analysis stats.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "status":'status',
        "message":'message',
        "stats":'stats'
    }

    def __init__(self,
                 status=None,
                 message=None,
                 stats=None):
        """Constructor for the DataTieringObjectAnalysisInfo class"""

        # Initialize members of the class
        self.status = status
        self.message = message
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
        status = dictionary.get('status')
        message = dictionary.get('message')
        stats = None
        if dictionary.get("stats") is not None:
            stats = list()
            for structure in dictionary.get('stats'):
                stats.append(cohesity_management_sdk.models_v2.data_tiering_share_stats.DataTieringShareStats.from_dictionary(structure))

        # Return an object of this model
        return cls(status,
                   message,
                   stats)


