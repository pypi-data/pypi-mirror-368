# -*- coding: utf-8 -*-


class PhysicalFileBackupPathParams(object):

    """Implementation of the 'PhysicalFileBackupPathParams' model.

    TODO: type model description here.

    Attributes:
        included_path (string): Specifies a path to be included on the source.
            All paths under this path will be included unless they are
            specifically mentioned in excluded paths.
        excluded_paths (list of string): Specifies a set of paths nested under
            the include path which should be excluded from the Protection
            Group.
        skip_nested_volumes (bool): Specifies whether to skip any nested
            volumes (both local and network) that are mounted under include
            path. Applicable only for windows sources.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "included_path":'includedPath',
        "excluded_paths":'excludedPaths',
        "skip_nested_volumes":'skipNestedVolumes'
    }

    def __init__(self,
                 included_path=None,
                 excluded_paths=None,
                 skip_nested_volumes=None):
        """Constructor for the PhysicalFileBackupPathParams class"""

        # Initialize members of the class
        self.included_path = included_path
        self.excluded_paths = excluded_paths
        self.skip_nested_volumes = skip_nested_volumes


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
        included_path = dictionary.get('includedPath')
        excluded_paths = dictionary.get('excludedPaths')
        skip_nested_volumes = dictionary.get('skipNestedVolumes')

        # Return an object of this model
        return cls(included_path,
                   excluded_paths,
                   skip_nested_volumes)


