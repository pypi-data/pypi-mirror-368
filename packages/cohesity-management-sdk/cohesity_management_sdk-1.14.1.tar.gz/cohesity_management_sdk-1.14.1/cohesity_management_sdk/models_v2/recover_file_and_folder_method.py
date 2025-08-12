# -*- coding: utf-8 -*-


class RecoverFileAndFolderMethod(object):

    """Implementation of the 'Recover File and Folder Method' model.

    Recover File and Folder Method

    Attributes:
        recover_file_and_folder_method (RecoverFileAndFolderMethod1Enum):
            Recover File and Folder Method.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recover_file_and_folder_method":'recoverFileAndFolderMethod'
    }

    def __init__(self,
                 recover_file_and_folder_method=None):
        """Constructor for the RecoverFileAndFolderMethod class"""

        # Initialize members of the class
        self.recover_file_and_folder_method = recover_file_and_folder_method


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
        recover_file_and_folder_method = dictionary.get('recoverFileAndFolderMethod')

        # Return an object of this model
        return cls(recover_file_and_folder_method)


