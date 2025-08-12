# -*- coding: utf-8 -*-


class SwiftConfig(object):

    """Implementation of the 'SwiftConfig' model.

    Specifies the Swift config settings for this View.

    Attributes:
        swift_user_domain (string): Specifies the Keystone user domain.
        swift_username (string): Specifies the Keystone username.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "swift_user_domain":'swiftUserDomain',
        "swift_username":'swiftUsername'
    }

    def __init__(self,
                 swift_user_domain=None,
                 swift_username=None):
        """Constructor for the SwiftConfig class"""

        # Initialize members of the class
        self.swift_user_domain = swift_user_domain
        self.swift_username = swift_username


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
        swift_user_domain = dictionary.get('swiftUserDomain')
        swift_username = dictionary.get('swiftUsername')

        # Return an object of this model
        return cls(swift_user_domain,
                   swift_username)


