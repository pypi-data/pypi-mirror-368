# -*- coding: utf-8 -*-


class EnumerationOfAllTheDocumentFilterOption(object):

    """Implementation of the 'Enumeration of all the document filter option.' model.

    Enumeration of all the document filter option.

    Attributes:
        documents_filter_type (DocumentsFilterTypeEnum): Enumeration of all
            the document filter option.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "documents_filter_type":'DocumentsFilterType'
    }

    def __init__(self,
                 documents_filter_type=None):
        """Constructor for the EnumerationOfAllTheDocumentFilterOption class"""

        # Initialize members of the class
        self.documents_filter_type = documents_filter_type


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
        documents_filter_type = dictionary.get('DocumentsFilterType')

        # Return an object of this model
        return cls(documents_filter_type)


