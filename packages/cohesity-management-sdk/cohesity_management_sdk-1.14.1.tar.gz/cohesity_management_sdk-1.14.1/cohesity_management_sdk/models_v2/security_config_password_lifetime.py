# -*- coding: utf-8 -*-


class SecurityConfigPasswordLifetime(object):

    """Implementation of the 'SecurityConfigPasswordLifetime' model.

    Specifies security config for password lifetime.

    Attributes:
        min_lifetime_days (int): Specifies the minimum password lifetime in
            days.
        max_lifetime_days (int): Specifies the maximum password lifetime in
            days.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "min_lifetime_days":'minLifetimeDays',
        "max_lifetime_days":'maxLifetimeDays'
    }

    def __init__(self,
                 min_lifetime_days=None,
                 max_lifetime_days=None):
        """Constructor for the SecurityConfigPasswordLifetime class"""

        # Initialize members of the class
        self.min_lifetime_days = min_lifetime_days
        self.max_lifetime_days = max_lifetime_days


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
        min_lifetime_days = dictionary.get('minLifetimeDays')
        max_lifetime_days = dictionary.get('maxLifetimeDays')

        # Return an object of this model
        return cls(min_lifetime_days,
                   max_lifetime_days)


