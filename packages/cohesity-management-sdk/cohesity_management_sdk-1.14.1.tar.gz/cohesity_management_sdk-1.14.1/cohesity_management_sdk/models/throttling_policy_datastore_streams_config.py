# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class ThrottlingPolicy_DatastoreStreamsConfig(object):

    """Implementation of the 'ThrottlingPolicy_DatastoreStreamsConfig' model.

    Attributes:
        max_concurrent_streams (int): If this value is > 0 and the number of
            streams concurrently active on a datastore is equal to it, then any
            further requests to access the
            datastore would be denied until the number of active streams reduces.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "max_concurrent_streams":'maxConcurrentStreams'
    }

    def __init__(self,
                 max_concurrent_streams=None):
        """Constructor for the ThrottlingPolicy_DatastoreStreamsConfig class"""

        # Initialize members of the class
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
        max_concurrent_streams = dictionary.get('maxConcurrentStreams')

        # Return an object of this model
        return cls(max_concurrent_streams)


