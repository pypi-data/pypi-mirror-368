# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.down_tiering_file_selection
import cohesity_management_sdk.models_v2.file_size_rule

class DownTieringExclusionPolicy(object):

    """Implementation of the 'DownTieringExclusionPolicy' model.

    Specifies the files exclusion rules for downtiering.

    Attributes:
        file_type (list of string): TODO: type description here.
        selection (DownTieringFileSelection): Specifies the file's selection
            rule for downtiering.
        file_size (FileSizeRule): Specifies the file's selection rule by file
            size. eg. 1. select files greather than 10 Bytes. 2. select files
            less than 20 TiB. 3. select files greather than 5 MiB. type:
            "object"

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "file_type":'fileType',
        "selection":'selection',
        "file_size":'fileSize'
    }

    def __init__(self,
                 file_type=None,
                 selection=None,
                 file_size=None):
        """Constructor for the DownTieringExclusionPolicy class"""

        # Initialize members of the class
        self.file_type = file_type
        self.selection = selection
        self.file_size = file_size


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
        selection = cohesity_management_sdk.models_v2.down_tiering_file_selection.DownTieringFileSelection.from_dictionary(dictionary.get('selection')) if dictionary.get('selection') else None
        file_size = cohesity_management_sdk.models_v2.file_size_rule.FileSizeRule.from_dictionary(dictionary.get('fileSize')) if dictionary.get('fileSize') else None

        # Return an object of this model
        return cls(file_type,
                   selection,
                   file_size)


