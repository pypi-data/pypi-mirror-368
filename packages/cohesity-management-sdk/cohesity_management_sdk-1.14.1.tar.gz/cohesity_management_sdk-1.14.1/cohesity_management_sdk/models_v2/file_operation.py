# -*- coding: utf-8 -*-


class FileOperation(object):

    """Implementation of the 'FileOperation' model.

    Attributes:
        file_path (string): TODO Type description here.
        operation (OperationEnum): TODO Type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "file_path":'filePath',
        "operation":'operation'
    }

    def __init__(self,
                 file_path=None,
                 operation=None):
        """Constructor for the FileOperation class"""

        # Initialize members of the class
        self.file_path = file_path
        self.operation = operation


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
        file_path = dictionary.get('filePath')
        operation = dictionary.get('operation')

        # Return an object of this model
        return cls(file_path,
                   operation)


