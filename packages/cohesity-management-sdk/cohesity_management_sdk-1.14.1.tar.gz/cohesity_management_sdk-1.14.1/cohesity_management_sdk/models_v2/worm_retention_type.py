# -*- coding: utf-8 -*-


class WormRetentionType(object):

    """Implementation of the 'Worm Retention type.' model.

    Worm Retention type.

    Attributes:
        worm_retention (WormRetentionEnum): Specifies Worm Retention type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "worm_retention":'wormRetention'
    }

    def __init__(self,
                 worm_retention=None):
        """Constructor for the WormRetentionType class"""

        # Initialize members of the class
        self.worm_retention = worm_retention


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
        worm_retention = dictionary.get('wormRetention')

        # Return an object of this model
        return cls(worm_retention)


