# -*- coding: utf-8 -*-


class SpecifiesLabelAndValueOfTags(object):

    """Implementation of the 'Specifies label and value of tags.' model.

    TODO: type model description here.

    Attributes:
        label (string): Specifies label of tag.
        value (string): Specifies value of tag.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "label":'label',
        "value":'value'
    }

    def __init__(self,
                 label=None,
                 value=None):
        """Constructor for the SpecifiesLabelAndValueOfTags class"""

        # Initialize members of the class
        self.label = label
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
        label = dictionary.get('label')
        value = dictionary.get('value')

        # Return an object of this model
        return cls(label,
                   value)


