# -*- coding: utf-8 -*-


class SecurityConfigPasswordReuse(object):

    """Implementation of the 'SecurityConfigPasswordReuse' model.

    Specifies security config for password reuse.

    Attributes:
        num_disallowed_old_passwords (int): Specifies the minimum number of
            old passwords that are not allowed for changing the password.
        num_different_chars (int): Specifies the number of characters in the
            new password that needs to be different from the old password
            (only applicable when changing the user's own password).

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "num_disallowed_old_passwords":'numDisallowedOldPasswords',
        "num_different_chars":'numDifferentChars'
    }

    def __init__(self,
                 num_disallowed_old_passwords=None,
                 num_different_chars=None):
        """Constructor for the SecurityConfigPasswordReuse class"""

        # Initialize members of the class
        self.num_disallowed_old_passwords = num_disallowed_old_passwords
        self.num_different_chars = num_different_chars


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
        num_disallowed_old_passwords = dictionary.get('numDisallowedOldPasswords')
        num_different_chars = dictionary.get('numDifferentChars')

        # Return an object of this model
        return cls(num_disallowed_old_passwords,
                   num_different_chars)


