# -*- coding: utf-8 -*-


class IndexingPolicy(object):

    """Implementation of the 'Indexing Policy.' model.

    Specifies settings for indexing files found in an Object (such as a VM) so
    these files can be searched and recovered. This also specifies inclusion
    and exclusion rules that determine the directories to index.

    Attributes:
        enable_indexing (bool): Specifies if the files found in an Object
            (such as a VM) should be indexed. If true (the default), files are
            indexed.
        include_paths (list of string): Array of Indexed Directories.
            Specifies a list of directories to index. Regular expression can
            also be specified to provide the directory paths. Example:
            /Users/<wildcard>/AppData
        exclude_paths (list of string): Array of Excluded Directories.
            Specifies a list of directories to exclude from indexing.Regular
            expression can also be specified to provide the directory paths.
            Example: /Users/<wildcard>/AppData

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enable_indexing":'enableIndexing',
        "include_paths":'includePaths',
        "exclude_paths":'excludePaths'
    }

    def __init__(self,
                 enable_indexing=None,
                 include_paths=None,
                 exclude_paths=None):
        """Constructor for the IndexingPolicy class"""

        # Initialize members of the class
        self.enable_indexing = enable_indexing
        self.include_paths = include_paths
        self.exclude_paths = exclude_paths


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
        enable_indexing = dictionary.get('enableIndexing')
        include_paths = dictionary.get('includePaths')
        exclude_paths = dictionary.get('excludePaths')

        # Return an object of this model
        return cls(enable_indexing,
                   include_paths,
                   exclude_paths)


