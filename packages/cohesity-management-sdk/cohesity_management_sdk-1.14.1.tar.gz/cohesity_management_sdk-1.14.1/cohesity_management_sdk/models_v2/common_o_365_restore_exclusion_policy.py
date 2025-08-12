# -*- coding: utf-8 -*-


class CommonO365RestoreExclusionPolicy(object):

    """Implementation of the 'CommonO365RestoreExclusionPolicy' model.

    Specifies the common filter policy to be applied for item exclusions
      in Microsoft 365 restore.

    Attributes:
        exclude_after_time_secs (long|int): Any items after this time will be excluded from restore. The
          time is specified as number of seconds after snapshot time.
        exclude_all (bool): All items will be excluded from restore.
        exclude_before_time_secs (bool): Any items before this time will be excluded from restore. The
          time is specified as number of seconds before snapshot time.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "exclude_after_time_secs":'excludeAfterTimeSecs',
        "exclude_all":'excludeAll',
        "exclude_before_time_secs":'excludeBeforeTimeSecs'
    }

    def __init__(self,
                 exclude_after_time_secs=None,
                 exclude_all=None,
                 exclude_before_time_secs=None):
        """Constructor for the CommonO365RestoreExclusionPolicy class"""

        # Initialize members of the class
        self.exclude_after_time_secs = exclude_after_time_secs
        self.exclude_all = exclude_all
        self.exclude_before_time_secs = exclude_before_time_secs


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
        exclude_after_time_secs = dictionary.get('excludeAfterTimeSecs')
        exclude_all = dictionary.get('excludeAll')
        exclude_before_time_secs = dictionary.get('excludeBeforeTimeSecs')


        # Return an object of this model
        return cls(exclude_after_time_secs,
                   exclude_all,
                   exclude_before_time_secs)