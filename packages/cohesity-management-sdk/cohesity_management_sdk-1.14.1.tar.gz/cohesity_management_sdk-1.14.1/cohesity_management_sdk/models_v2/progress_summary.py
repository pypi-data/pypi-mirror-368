# -*- coding: utf-8 -*-


class ProgressSummary(object):

    """Implementation of the 'ProgressSummary' model.

    Specifies the progress summary.

    Attributes:
        success (long|int): Specifies the successful count.
        failed (long|int): Specifies the failed count.
        total (long|int): Specifies the total count.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "success":'success',
        "failed":'failed',
        "total":'total'
    }

    def __init__(self,
                 success=None,
                 failed=None,
                 total=None):
        """Constructor for the ProgressSummary class"""

        # Initialize members of the class
        self.success = success
        self.failed = failed
        self.total = total


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
        success = dictionary.get('success')
        failed = dictionary.get('failed')
        total = dictionary.get('total')

        # Return an object of this model
        return cls(success,
                   failed,
                   total)


