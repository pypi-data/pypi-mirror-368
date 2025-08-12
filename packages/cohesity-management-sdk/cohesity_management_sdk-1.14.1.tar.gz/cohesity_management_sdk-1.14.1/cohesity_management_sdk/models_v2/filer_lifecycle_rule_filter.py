# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.filer_lifecycle_size_filter

class FilerLifecycleRuleFilter(object):

    """Implementation of the 'FilerLifecycleRuleFilter' model.

    Specifies the filter used to identify files that a Lifecycle Rule
      applies to.

    Attributes:
        file_extensions (list of string): Specifies the file''s selection based on their extension. Eg:
          .pdf, .txt, etc. Note: Provide extensions here with the initial ''.'' character,
          example .pdf and not pdf. Extensions are case-insensitive, i.e. .pdf extension
          in filter will delete all files have .pdf, .PDF, .pDF, etc.
        file_size (FilerLifecycleSizeFilter): Specifies the file's selection based on their size.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "file_extensions":'fileExtensions',
        "file_size":'fileSize'
    }

    def __init__(self,
                 file_extensions=None,
                 file_size=None):
        """Constructor for the FilerLifecycleRuleFilter class"""

        # Initialize members of the class
        self.file_extensions = file_extensions
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
        file_extensions = dictionary.get('fileExtensions')
        file_size = cohesity_management_sdk.models_v2.filer_lifecycle_size_filter.FilerLifecycleSizeFilter.from_dictionary(dictionary.get('fileSize')) if dictionary.get('fileSize') else None

        # Return an object of this model
        return cls(file_extensions,
                   file_size)