# -*- coding: utf-8 -*-


class ResponseWithTwoListsAListOfEnabledCiphersAndAListOfDisabledCiphers(object):

    """Implementation of the 'Response with two lists: a list of enabled ciphers and a list of disabled ciphers.' model.

    Specifies a list of enabled/disabled ciphers on the cluster.

    Attributes:
        enabled_ciphers (list of string): Enabled ciphers.
        disabled_ciphers (list of string): Disabled ciphers.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enabled_ciphers":'enabledCiphers',
        "disabled_ciphers":'disabledCiphers'
    }

    def __init__(self,
                 enabled_ciphers=None,
                 disabled_ciphers=None):
        """Constructor for the ResponseWithTwoListsAListOfEnabledCiphersAndAListOfDisabledCiphers class"""

        # Initialize members of the class
        self.enabled_ciphers = enabled_ciphers
        self.disabled_ciphers = disabled_ciphers


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
        enabled_ciphers = dictionary.get('enabledCiphers')
        disabled_ciphers = dictionary.get('disabledCiphers')

        # Return an object of this model
        return cls(enabled_ciphers,
                   disabled_ciphers)


