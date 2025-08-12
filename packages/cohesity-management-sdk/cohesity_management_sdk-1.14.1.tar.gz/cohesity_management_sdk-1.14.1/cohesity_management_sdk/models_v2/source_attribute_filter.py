# -*- coding: utf-8 -*-


class SourceAttributeFilter(object):

    """Implementation of the 'SourceAttributeFilter' model.

    Specifies a pair of source filter attribute and its possible values.

    Attributes:
        filter_attribute (string): Specifies the filter attribute for the
            source.
        attribute_values (list of string): Specifies the list of attribute
            values for above filter.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "filter_attribute":'filterAttribute',
        "attribute_values":'attributeValues'
    }

    def __init__(self,
                 filter_attribute=None,
                 attribute_values=None):
        """Constructor for the SourceAttributeFilter class"""

        # Initialize members of the class
        self.filter_attribute = filter_attribute
        self.attribute_values = attribute_values


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
        filter_attribute = dictionary.get('filterAttribute')
        attribute_values = dictionary.get('attributeValues')

        # Return an object of this model
        return cls(filter_attribute,
                   attribute_values)


