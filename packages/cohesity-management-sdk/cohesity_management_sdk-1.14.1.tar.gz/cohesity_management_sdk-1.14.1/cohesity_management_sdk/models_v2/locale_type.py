# -*- coding: utf-8 -*-


class LocaleType(object):

    """Implementation of the 'Locale type.' model.

    Locale type.

    Attributes:
        locale (string): Specifies Locale type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "locale":'locale'
    }

    def __init__(self,
                 locale=None):
        """Constructor for the LocaleType class"""

        # Initialize members of the class
        self.locale = locale


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
        locale = dictionary.get('locale')

        # Return an object of this model
        return cls(locale)


