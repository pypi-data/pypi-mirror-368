# -*- coding: utf-8 -*-


class SecurityConfigPasswordStrength(object):

    """Implementation of the 'SecurityConfigPasswordStrength' model.

    Specifies security config for password strength.

    Attributes:
        min_length (int): Specifies the password minimum length.
        include_upper_letter (bool): Specifies if the password needs to have
            at least one uppercase letter.
        include_lower_letter (bool): Specifies if the password needs to have
            at least one lowercase letter.
        include_number (bool): Specifies if the password needs to have at
            least one number.
        include_special_char (bool): Specifies if the password needs to have
            at least one special character.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "min_length":'minLength',
        "include_upper_letter":'includeUpperLetter',
        "include_lower_letter":'includeLowerLetter',
        "include_number":'includeNumber',
        "include_special_char":'includeSpecialChar'
    }

    def __init__(self,
                 min_length=None,
                 include_upper_letter=None,
                 include_lower_letter=None,
                 include_number=None,
                 include_special_char=None):
        """Constructor for the SecurityConfigPasswordStrength class"""

        # Initialize members of the class
        self.min_length = min_length
        self.include_upper_letter = include_upper_letter
        self.include_lower_letter = include_lower_letter
        self.include_number = include_number
        self.include_special_char = include_special_char


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
        min_length = dictionary.get('minLength')
        include_upper_letter = dictionary.get('includeUpperLetter')
        include_lower_letter = dictionary.get('includeLowerLetter')
        include_number = dictionary.get('includeNumber')
        include_special_char = dictionary.get('includeSpecialChar')

        # Return an object of this model
        return cls(min_length,
                   include_upper_letter,
                   include_lower_letter,
                   include_number,
                   include_special_char)


