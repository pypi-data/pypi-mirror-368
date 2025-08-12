# -*- coding: utf-8 -*-


class ExchangeParams(object):

    """Implementation of the 'ExchangeParams' model.

    Specifies the parameters which are specific for searching Exchange
    mailboxes.

    Attributes:
        search_string (string): Specifies the search string to search the
            Exchange Objects

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "search_string":'searchString'
    }

    def __init__(self,
                 search_string=None):
        """Constructor for the ExchangeParams class"""

        # Initialize members of the class
        self.search_string = search_string


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
        search_string = dictionary.get('searchString')

        # Return an object of this model
        return cls(search_string)


