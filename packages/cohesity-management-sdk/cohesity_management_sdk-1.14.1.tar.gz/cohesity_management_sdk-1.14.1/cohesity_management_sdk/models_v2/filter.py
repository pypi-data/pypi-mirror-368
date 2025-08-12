# -*- coding: utf-8 -*-


class Filter(object):

    """Implementation of the 'Filter' model.

    Specifies the filter details.

    Attributes:
        filter_string (string): Specifies the filter string using wildcard
            supported strings or regular expressions.
        is_regular_expression (bool): Specifies whether the provided filter
            string is a regular expression or not. This need to be explicitly
            set to true if user is trying to filter by regular expressions.
            Not providing this value in case of regular expression can result
            in unintended results. The default value is assumed to be false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "filter_string":'filterString',
        "is_regular_expression":'isRegularExpression'
    }

    def __init__(self,
                 filter_string=None,
                 is_regular_expression=False):
        """Constructor for the Filter class"""

        # Initialize members of the class
        self.filter_string = filter_string
        self.is_regular_expression = is_regular_expression


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
        filter_string = dictionary.get('filterString')
        is_regular_expression = dictionary.get("isRegularExpression") if dictionary.get("isRegularExpression") else False

        # Return an object of this model
        return cls(filter_string,
                   is_regular_expression)


