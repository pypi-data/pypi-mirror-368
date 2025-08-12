# -*- coding: utf-8 -*-


class CouchbaseParams(object):

    """Implementation of the 'CouchbaseParams' model.

    Specifies the parameters which are specific for searching Couchbase
    objects.

    Attributes:
        couchbase_object_types (list of CouchbaseObjectTypeEnum): Specifies
            Couchbase object types be searched. For Couchbase it can only be
            set to 'CouchbaseBuckets'.
        search_string (string): Specifies the search string to search the
            Couchbase Objects
        source_ids (list of long|int): Specifies a list of source ids. Only
            objects found in these sources will be returned.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "couchbase_object_types":'couchbaseObjectTypes',
        "search_string":'searchString',
        "source_ids":'sourceIds'
    }

    def __init__(self,
                 couchbase_object_types=None,
                 search_string=None,
                 source_ids=None):
        """Constructor for the CouchbaseParams class"""

        # Initialize members of the class
        self.couchbase_object_types = couchbase_object_types
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
        couchbase_object_types = dictionary.get('couchbaseObjectTypes')
        search_string = dictionary.get('searchString')
        source_ids = dictionary.get('sourceIds')

        # Return an object of this model
        return cls(couchbase_object_types,
                   search_string,
                   source_ids)


