# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.progress_summary
import cohesity_management_sdk.models_v2.data_tiering_task_stats

class TieringInfo(object):

    """Implementation of the 'TieringInfo' model.

    Specifies the data tiering task details.

    Attributes:
        progress (ProgressSummary): Specifies the progress summary.
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
        stats (DataTieringTaskStats): Specifies the stats of data tiering
            task.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "progress":'progress',
        "status":'status',
        "stats":'stats'
    }

    def __init__(self,
                 progress=None,
                 status=None,
                 stats=None):
        """Constructor for the TieringInfo class"""

        # Initialize members of the class
        self.progress = progress
        self.status = status
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
        progress = cohesity_management_sdk.models_v2.progress_summary.ProgressSummary.from_dictionary(dictionary.get('progress')) if dictionary.get('progress') else None
        status = dictionary.get('status')
        stats = cohesity_management_sdk.models_v2.data_tiering_task_stats.DataTieringTaskStats.from_dictionary(dictionary.get('stats')) if dictionary.get('stats') else None

        # Return an object of this model
        return cls(progress,
                   status,
                   stats)


