# -*- coding: utf-8 -*-


class FileTypeRule(object):

    """Implementation of the 'FileTypeRule' model.

    Specifies the list of files types.

    Attributes:
        file_type (list of string): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "file_type":'fileType'
    }

    def __init__(self,
                 file_type=None):
        """Constructor for the FileTypeRule class"""

        # Initialize members of the class
        self.file_type = file_type


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
        file_type = dictionary.get('fileType')

        # Return an object of this model
        return cls(file_type)


