# -*- coding: utf-8 -*-


class NonCurrentVersionExpirationAction(object):

    """Implementation of the 'NonCurrentVersionExpirationAction' model.

    Specifies the Lifecycle Non-current Version Expiration Action.

    Attributes:
        days (long|int64): Specifies the number of days an object is non-current before
          performing the associated action.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "days":'days'
    }

    def __init__(self,
                 days=None):
        """Constructor for the NonCurrentVersionExpirationAction class"""

        # Initialize members of the class
        self.days = days


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
        days = dictionary.get('days')

        # Return an object of this model
        return cls(days)