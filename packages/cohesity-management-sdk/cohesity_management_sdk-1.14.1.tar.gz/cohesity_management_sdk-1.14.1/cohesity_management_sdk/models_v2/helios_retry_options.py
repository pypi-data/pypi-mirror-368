# -*- coding: utf-8 -*-


class HeliosRetryOptions(object):

    """Implementation of the 'HeliosRetryOptions' model.

    Retry Options of a Protection Policy when a Protection Group run fails.

    Attributes:
        retries (int): Specifies the number of times to retry capturing
            Snapshots before the Protection Group Run fails.
        retry_interval_mins (int): Specifies the number of minutes before
            retrying a failed Protection Group.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "retries":'retries',
        "retry_interval_mins":'retryIntervalMins'
    }

    def __init__(self,
                 retries=None,
                 retry_interval_mins=None):
        """Constructor for the HeliosRetryOptions class"""

        # Initialize members of the class
        self.retries = retries
        self.retry_interval_mins = retry_interval_mins


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
        retries = dictionary.get('retries')
        retry_interval_mins = dictionary.get('retryIntervalMins')

        # Return an object of this model
        return cls(retries,
                   retry_interval_mins)


