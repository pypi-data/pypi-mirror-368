# -*- coding: utf-8 -*-


class ExchangeServerAuthMethod(object):

    """Implementation of the 'ExchangeServerAuthMethod' model.

    Specifies the Exchange Server auth method

    Attributes:
        value (ValueEnum): Specifies the Exchange Server auth method.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "value":'value'
    }

    def __init__(self,
                 value=None):
        """Constructor for the ExchangeServerAuthMethod class"""

        # Initialize members of the class
        self.value = value


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
        value = dictionary.get('value')

        # Return an object of this model
        return cls(value)