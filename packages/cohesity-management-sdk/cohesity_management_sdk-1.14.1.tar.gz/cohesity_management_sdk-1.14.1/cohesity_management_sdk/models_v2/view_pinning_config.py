# -*- coding: utf-8 -*-


class ViewPinningConfig(object):

    """Implementation of the 'ViewPinningConfig' model.

    Specifies the pinning config of a view.

    Attributes:
        enabled (bool):  Specifies if view pinning is enabled. If set to true,
            view will be pinned to SSD and view data will be stored there.
        pinned_time_secs (long|int): Specifies the time to pin files after last
            access.
        last_updated_timestamp_secs (long|int): Specifies the timestamp when
            view pinning config is last updated.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enabled":'enabled',
        "pinned_time_secs":'pinnedTimeSecs',
        "last_updated_timestamp_secs":'lastUpdatedTimestampSecs'
    }

    def __init__(self,
                 enabled=None,
                 pinned_time_secs=None,
                 last_updated_timestamp_secs=None):
        """Constructor for the ViewPinningConfig class"""

        # Initialize members of the class
        self.enabled = enabled
        self.pinned_time_secs = pinned_time_secs
        self.last_updated_timestamp_secs = last_updated_timestamp_secs


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
        enabled = dictionary.get('enabled')
        pinned_time_secs = dictionary.get('pinnedTimeSecs')
        last_updated_timestamp_secs = dictionary.get('lastUpdatedTimestampSecs')

        # Return an object of this model
        return cls(enabled,
                   pinned_time_secs,
                   last_updated_timestamp_secs)


