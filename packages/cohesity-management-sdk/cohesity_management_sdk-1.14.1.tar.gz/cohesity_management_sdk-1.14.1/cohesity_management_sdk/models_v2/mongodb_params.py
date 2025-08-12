# -*- coding: utf-8 -*-


class MongodbParams(object):

    """Implementation of the 'MongodbParams' model.

    Specifies the parameters which are specific for searching MongoDB
    objects.

    Attributes:
        mongo_db_object_types (list of MongoDBObjectTypeEnum): Specifies one
            or more MongoDB object types be searched.
        search_string (string): Specifies the search string to search the
            MongoDB Objects
        source_ids (list of long|int): Specifies a list of source ids. Only
            objects found in these sources will be returned.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "search_string":'searchString',
        "mongo_db_object_types":'mongoDBObjectTypes',
        "source_ids":'sourceIds'
    }

    def __init__(self,
                 search_string=None,
                 mongo_db_object_types=None,
                 source_ids=None):
        """Constructor for the MongodbParams class"""

        # Initialize members of the class
        self.mongo_db_object_types = mongo_db_object_types
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
        mongo_db_object_types = dictionary.get('mongoDBObjectTypes')
        source_ids = dictionary.get('sourceIds')

        # Return an object of this model
        return cls(search_string,
                   mongo_db_object_types,
                   source_ids)


