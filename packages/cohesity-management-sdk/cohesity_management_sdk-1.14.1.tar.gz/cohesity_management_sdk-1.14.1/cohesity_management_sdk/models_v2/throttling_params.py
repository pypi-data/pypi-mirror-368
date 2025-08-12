# -*- coding: utf-8 -*-


class ThrottlingParams(object):

    """Implementation of the 'Throttling Params.' model.

    Specifies throttling params.

    Attributes:
        new_task_latency_threshold_msecs (long|int): If the latency of a
            datastore is above this value, then a new backup task that uses
            the datastore won't be started.
        max_concurrent_backups (long|int): Specifies the number of VMs of a vCenter that can be backed up
          concurrently.
        active_task_latency_threshold_msecs (long|int): If the latency of a
            datastore is above this value, then an existing backup task that
            uses the datastore will start getting throttled.
        max_concurrent_streams (int): If this value is > 0 and the number of
            streams concurrently active on a datastore is equal to it, then
            any further requests to access the datastore would be denied until
            the number of active streams reduces. This applies for all the
            datastores in the specified host.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "new_task_latency_threshold_msecs":'newTaskLatencyThresholdMsecs',
        "max_concurrent_backups":'maxConcurrentBackups',
        "active_task_latency_threshold_msecs":'activeTaskLatencyThresholdMsecs',
        "max_concurrent_streams":'maxConcurrentStreams'
    }

    def __init__(self,
                 new_task_latency_threshold_msecs=None,
                 max_concurrent_backups=None,
                 active_task_latency_threshold_msecs=None,
                 max_concurrent_streams=None):
        """Constructor for the ThrottlingParams class"""

        # Initialize members of the class
        self.new_task_latency_threshold_msecs = new_task_latency_threshold_msecs
        self.max_concurrent_backups = max_concurrent_backups
        self.active_task_latency_threshold_msecs = active_task_latency_threshold_msecs
        self.max_concurrent_streams = max_concurrent_streams


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
        new_task_latency_threshold_msecs = dictionary.get('newTaskLatencyThresholdMsecs')
        max_concurrent_backups = dictionary.get('maxConcurrentBackups')
        active_task_latency_threshold_msecs = dictionary.get('activeTaskLatencyThresholdMsecs')
        max_concurrent_streams = dictionary.get('maxConcurrentStreams')

        # Return an object of this model
        return cls(new_task_latency_threshold_msecs,
                   max_concurrent_backups,
                   active_task_latency_threshold_msecs,
                   max_concurrent_streams)