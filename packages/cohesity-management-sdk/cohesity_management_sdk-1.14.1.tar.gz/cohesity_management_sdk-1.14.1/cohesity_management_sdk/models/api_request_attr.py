# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class APIRequestAttr(object):

    """Implementation of the 'APIRequestAttr' model.

    Attributes:
        timeout_secs (int): The timeout to be used with this request. If specified
            (> 0), the request will be timed out if it has been waiting in the
            queue for longer than this value.
        type (int):  Specifies the request type.
        use_read_replica (bool): Indicates whether this request should be sent to read replica.
            Data served by read replica will be lagging Magneto master by a small
            duration. The decision to re-route to read replica is actually made
            by the magneto-service go client, not Magneto master

            Why we chose to have it here

            1) Go magneto service does not support default parameters.

            2) We did not want to change the magneto service function signatures to

            include new variable.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "timeout_secs": 'timeoutSecs',
        "type": 'type',
        "use_read_replica": 'useReadReplica'
    }

    def __init__(self,
                 timeout_secs=None,
                 type=None,
                 use_read_replica=None):
        """Constructor for the APIRequestAttr class"""

        # Initialize members of the class
        self.timeout_secs = timeout_secs
        self.type = type
        self.use_read_replica = use_read_replica


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
        timeout_secs = dictionary.get('timeoutSecs')
        type = dictionary.get('type', None)
        use_read_replica = dictionary.get('useReadReplica', None)

        # Return an object of this model
        return cls(timeout_secs,
                   type,
                   use_read_replica)


