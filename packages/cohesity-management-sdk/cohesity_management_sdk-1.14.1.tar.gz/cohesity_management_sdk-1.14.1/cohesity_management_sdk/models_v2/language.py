# -*- coding: utf-8 -*-


class Language(object):

    """Implementation of the 'Language' model.

    Language

    Attributes:
        language (Language2Enum): Specifies the language.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "language":'language'
    }

    def __init__(self,
                 language=None):
        """Constructor for the Language class"""

        # Initialize members of the class
        self.language = language


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
        language = dictionary.get('language')

        # Return an object of this model
        return cls(language)


