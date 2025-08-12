# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.up_tiering_file_selection
import cohesity_management_sdk.models_v2.file_size_rule

class UpTieringInclusionPolicy(object):

    """Implementation of the 'UpTieringInclusionPolicy' model.

    Specifies the files selection rules for uptiering.

    Attributes:
        file_type (list of string): TODO: type description here.
        selection (UpTieringFileSelection): Specifies the file's selection
            rule for uptiering.
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
        """Constructor for the UpTieringInclusionPolicy class"""

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
        selection = cohesity_management_sdk.models_v2.up_tiering_file_selection.UpTieringFileSelection.from_dictionary(dictionary.get('selection')) if dictionary.get('selection') else None
        file_size = cohesity_management_sdk.models_v2.file_size_rule.FileSizeRule.from_dictionary(dictionary.get('fileSize')) if dictionary.get('fileSize') else None

        # Return an object of this model
        return cls(file_type,
                   selection,
                   file_size)


