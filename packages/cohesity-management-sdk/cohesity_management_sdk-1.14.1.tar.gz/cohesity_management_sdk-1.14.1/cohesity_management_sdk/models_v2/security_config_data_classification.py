# -*- coding: utf-8 -*-


class SecurityConfigDataClassification(object):

    """Implementation of the 'SecurityConfigDataClassification' model.

    Specifies security config for data classification.

    Attributes:
        is_data_classified (bool): Specifies whether to mark the web page data
            classified/unclassified.
        classified_data_message (string): Specifies the classified data
            message.
        unclassified_data_message (string): Specifies the unclassified data
            message.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "is_data_classified":'isDataClassified',
        "classified_data_message":'classifiedDataMessage',
        "unclassified_data_message":'unclassifiedDataMessage'
    }

    def __init__(self,
                 is_data_classified=None,
                 classified_data_message=None,
                 unclassified_data_message=None):
        """Constructor for the SecurityConfigDataClassification class"""

        # Initialize members of the class
        self.is_data_classified = is_data_classified
        self.classified_data_message = classified_data_message
        self.unclassified_data_message = unclassified_data_message


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
        is_data_classified = dictionary.get('isDataClassified')
        classified_data_message = dictionary.get('classifiedDataMessage')
        unclassified_data_message = dictionary.get('unclassifiedDataMessage')

        # Return an object of this model
        return cls(is_data_classified,
                   classified_data_message,
                   unclassified_data_message)


