# -*- coding: utf-8 -*-


class DataTieringShareStats(object):

    """Implementation of the 'DataTieringShareStats' model.

    Specifies the source shares analysis stats.

    Attributes:
        file_type_tag (string): Specifies the file type bucket.
        file_size_tag (string): Specifies the file size bucket.
        access_time_tag (string): Specifies the access time bucket.
        mod_time_tag (string): Specifies the modification time bucket.
        file_count (int): Specifies the file count.
        total_size (int): Specifies the total count.
        id (int): Specifies the unique identifer for stat.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "file_type_tag":'fileTypeTag',
        "file_size_tag":'fileSizeTag',
        "access_time_tag":'accessTimeTag',
        "mod_time_tag":'modTimeTag',
        "file_count":'fileCount',
        "total_size":'totalSize',
        "id":'id'
    }

    def __init__(self,
                 file_type_tag=None,
                 file_size_tag=None,
                 access_time_tag=None,
                 mod_time_tag=None,
                 file_count=None,
                 total_size=None,
                 id=None):
        """Constructor for the DataTieringShareStats class"""

        # Initialize members of the class
        self.file_type_tag = file_type_tag
        self.file_size_tag = file_size_tag
        self.access_time_tag = access_time_tag
        self.mod_time_tag = mod_time_tag
        self.file_count = file_count
        self.total_size = total_size
        self.id = id


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
        file_type_tag = dictionary.get('fileTypeTag')
        file_size_tag = dictionary.get('fileSizeTag')
        access_time_tag = dictionary.get('accessTimeTag')
        mod_time_tag = dictionary.get('modTimeTag')
        file_count = dictionary.get('fileCount')
        total_size = dictionary.get('totalSize')
        id = dictionary.get('id')

        # Return an object of this model
        return cls(file_type_tag,
                   file_size_tag,
                   access_time_tag,
                   mod_time_tag,
                   file_count,
                   total_size,
                   id)


