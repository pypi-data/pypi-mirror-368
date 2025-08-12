# -*- coding: utf-8 -*-


class VMFilter(object):

    """Implementation of the 'VMFilter.' model.

    Specifies the VM filter details.

    Attributes:
        case_sensitive (bool): Specifies whether the provided filter string is case sensitive
            or not. This needs to be explicitly set to true if user is trying to filter
            by case sensitive expressions. The default value is assumed to be false.
        filter_string (string): Specifies the filter string using wildcard supported strings
          or regular expressions.
        is_regular_expression (bool): Specifies whether the provided filter string is a regular expression
          or not. This needs to be explicitly set to true if user is trying to filter
          by regular expressions. Not providing this value in case of regular expression
          can result in unintended results. The default value is assumed to be false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "case_sensitive":'caseSensitive',
        "filter_string":'filterString',
        "is_regular_expression":'isRegularExpression'
    }

    def __init__(self,
                 case_sensitive=None,
                 filter_string=None,
                 is_regular_expression=None):
        """Constructor for the VMfilter class"""

        # Initialize members of the class
        self.case_sensitive = case_sensitive
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
        case_sensitive = dictionary.get('caseSensitive')
        filter_string = dictionary.get('filterString')
        is_regular_expression = dictionary.get('isRegularExpression')


        # Return an object of this model
        return cls(case_sensitive,
                   filter_string,
                   is_regular_expression)