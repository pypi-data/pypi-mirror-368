# -*- coding: utf-8 -*-


class CassandraParams(object):

    """Implementation of the 'CassandraParams' model.

    Specifies the parameters which are specific for searching Cassandra
    objects.

    Attributes:
        cassandra_object_types (list of CassandraObjectTypeEnum): Specifies
            one or more Cassandra object types to be searched.
        search_string (string): Specifies the search string to search the
            Cassandra Objects
        source_ids (list of long|int): Specifies a list of source ids. Only
            objects found in these sources will be returned.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cassandra_object_types":'cassandraObjectTypes',
        "search_string":'searchString',
        "source_ids":'sourceIds'
    }

    def __init__(self,
                 cassandra_object_types=None,
                 search_string=None,
                 source_ids=None):
        """Constructor for the CassandraParams class"""

        # Initialize members of the class
        self.cassandra_object_types = cassandra_object_types
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
        cassandra_object_types = dictionary.get('cassandraObjectTypes')
        search_string = dictionary.get('searchString')
        source_ids = dictionary.get('sourceIds')

        # Return an object of this model
        return cls(cassandra_object_types,
                   search_string,
                   source_ids)


