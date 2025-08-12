# -*- coding: utf-8 -*-


class RecoverCouchbaseObjectParams1(object):

    """Implementation of the 'Recover Couchbase Object Params.1' model.

    Specifies the parameters to filter documents to be restored.

    Attributes:
        document_filter_type (DocumentFilterTypeEnum): Specifies the filter
            type for Documents to be restored.
        id_regex (string): A regular expression to match Documents ID's to be
            restored.
        filter_expression (string): A filter expression to match Documents
            content to be restored.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "document_filter_type":'documentFilterType',
        "id_regex":'idRegex',
        "filter_expression":'filterExpression'
    }

    def __init__(self,
                 document_filter_type=None,
                 id_regex=None,
                 filter_expression=None):
        """Constructor for the RecoverCouchbaseObjectParams1 class"""

        # Initialize members of the class
        self.document_filter_type = document_filter_type
        self.id_regex = id_regex
        self.filter_expression = filter_expression


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
        document_filter_type = dictionary.get('documentFilterType')
        id_regex = dictionary.get('idRegex')
        filter_expression = dictionary.get('filterExpression')

        # Return an object of this model
        return cls(document_filter_type,
                   id_regex,
                   filter_expression)


