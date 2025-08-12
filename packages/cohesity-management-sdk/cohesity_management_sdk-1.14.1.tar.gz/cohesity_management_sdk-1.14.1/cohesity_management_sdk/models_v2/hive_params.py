# -*- coding: utf-8 -*-


class HiveParams(object):

    """Implementation of the 'HiveParams' model.

    Specifies the parameters which are specific for searching Hive objects.

    Attributes:
        hive_object_types (list of HiveObjectTypeEnum): Specifies one or more
            Hive object types be searched.
        search_string (string): Specifies the search string to search the Hive
            Objects
        source_ids (list of long|int): Specifies a list of source ids. Only
            objects found in these sources will be returned.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "hive_object_types":'hiveObjectTypes',
        "search_string":'searchString',
        "source_ids":'sourceIds'
    }

    def __init__(self,
                 hive_object_types=None,
                 search_string=None,
                 source_ids=None):
        """Constructor for the HiveParams class"""

        # Initialize members of the class
        self.hive_object_types = hive_object_types
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
        hive_object_types = dictionary.get('hiveObjectTypes')
        search_string = dictionary.get('searchString')
        source_ids = dictionary.get('sourceIds')

        # Return an object of this model
        return cls(hive_object_types,
                   search_string,
                   source_ids)


