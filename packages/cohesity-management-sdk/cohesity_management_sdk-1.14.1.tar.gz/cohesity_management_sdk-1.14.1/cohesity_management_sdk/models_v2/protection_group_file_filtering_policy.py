# -*- coding: utf-8 -*-


class ProtectionGroupFileFilteringPolicy(object):

    """Implementation of the 'ProtectionGroupFileFilteringPolicy' model.

    Specifies a set of filters for a file based Protection Group. These values
    are strings which can represent a prefix or suffix. Example: '/tmp' or
    '*.mp4'. For file based Protection Groups, all files under prefixes
    specified by the 'includeFilters' list will be protected unless they are
    explicitly excluded by the 'excludeFilters' list.

    Attributes:
        include_list (list of string): Specifies the list of included files
            for this Protection Group.
        exclude_list (list of string): Specifies the list of excluded files
            for this protection Protection Group. Exclude filters have a
            higher priority than include filters.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "include_list":'includeList',
        "exclude_list":'excludeList'
    }

    def __init__(self,
                 include_list=None,
                 exclude_list=None):
        """Constructor for the ProtectionGroupFileFilteringPolicy class"""

        # Initialize members of the class
        self.include_list = include_list
        self.exclude_list = exclude_list


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
        include_list = dictionary.get('includeList')
        exclude_list = dictionary.get('excludeList')

        # Return an object of this model
        return cls(include_list,
                   exclude_list)


