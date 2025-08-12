# -*- coding: utf-8 -*-


class HdfsParams(object):

    """Implementation of the 'HdfsParams' model.

    Specifies the parameters for searching HDFS Folders and Files.

    Attributes:
        hdfs_types (list of HdfsTypeEnum): Specifies types as Folders or Files
            or both to be searched.
        search_string (string): Specifies the search string to search the HDFS
            Folders and Files.
        source_ids (list of long|int): Specifies a list of source ids. Only
            objects found in these sources will be returned.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "search_string":'searchString',
        "hdfs_types":'hdfsTypes',
        "source_ids":'sourceIds'
    }

    def __init__(self,
                 search_string=None,
                 hdfs_types=None,
                 source_ids=None):
        """Constructor for the HdfsParams class"""

        # Initialize members of the class
        self.hdfs_types = hdfs_types
        self.search_string = search_string
        self.source_ids = source_ids


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
        hdfs_types = dictionary.get('hdfsTypes')
        source_ids = dictionary.get('sourceIds')

        # Return an object of this model
        return cls(search_string,
                   hdfs_types,
                   source_ids)


