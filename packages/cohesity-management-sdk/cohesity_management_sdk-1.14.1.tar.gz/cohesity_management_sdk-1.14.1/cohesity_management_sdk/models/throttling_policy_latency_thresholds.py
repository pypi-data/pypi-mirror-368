# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class ThrottlingPolicy_LatencyThresholds(object):

    """Implementation of the 'ThrottlingPolicy_LatencyThresholds' model.

    Attributes:
        active_task_latency_threshold_msecs (long| int): If the latency of a
            datastore is above this value, then an existing
            backup task that uses the datastore will start getting throttled.
        new_task_latency_threshold_msecs (long| int): If the latency of a
            datastore is above this value, then a new backup
            task that uses the datastore won''t be started.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "active_task_latency_threshold_msecs": 'activeTaskLatencyThresholdMsecs',
        "new_task_latency_threshold_msecs": 'newTaskLatencyThresholdMsecs'
    }

    def __init__(self,
                 active_task_latency_threshold_msecs=None,
                 new_task_latency_threshold_msecs=None):
        """Constructor for the ThrottlingPolicy_LatencyThresholds class"""

        # Initialize members of the class
        self.active_task_latency_threshold_msecs = active_task_latency_threshold_msecs
        self.new_task_latency_threshold_msecs = new_task_latency_threshold_msecs


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
        active_task_latency_threshold_msecs = dictionary.get('activeTaskLatencyThresholdMsecs', None)
        new_task_latency_threshold_msecs = dictionary.get('newTaskLatencyThresholdMsecs', None)

        # Return an object of this model
        return cls(active_task_latency_threshold_msecs,
                   new_task_latency_threshold_msecs)


