# -*- coding: utf-8 -*-


class SearchFilesRequestParams(object):

    """Implementation of the 'Search files request params.' model.

    Specifies the request parameters to search for files and file folders.

    Attributes:
        search_string (string): Specifies the search string to filter the
            files. User can specify a wildcard character '*' as a suffix to a
            string where all files name are matched with the prefix string.
        types (list of Type30Enum): Specifies a list of file types. Only files
            within the given types will be returned.
        source_environments (list of SourceEnvironment1Enum): Specifies a list
            of the source environments. Only files from these types of source
            will be returned.
        source_ids (list of long|int): Specifies a list of source ids. Only
            files found in these sources will be returned.
        object_ids (list of long|int): Specifies a list of object ids. Only
            files found in these objects will be returned.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "search_string":'searchString',
        "types":'types',
        "source_environments":'sourceEnvironments',
        "source_ids":'sourceIds',
        "object_ids":'objectIds'
    }

    def __init__(self,
                 search_string=None,
                 types=None,
                 source_environments=None,
                 source_ids=None,
                 object_ids=None):
        """Constructor for the SearchFilesRequestParams class"""

        # Initialize members of the class
        self.search_string = search_string
        self.types = types
        self.source_environments = source_environments
        self.source_ids = source_ids
        self.object_ids = object_ids


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
        search_string = dictionary.get('searchString')
        types = dictionary.get('types')
        source_environments = dictionary.get('sourceEnvironments')
        source_ids = dictionary.get('sourceIds')
        object_ids = dictionary.get('objectIds')

        # Return an object of this model
        return cls(search_string,
                   types,
                   source_environments,
                   source_ids,
                   object_ids)


