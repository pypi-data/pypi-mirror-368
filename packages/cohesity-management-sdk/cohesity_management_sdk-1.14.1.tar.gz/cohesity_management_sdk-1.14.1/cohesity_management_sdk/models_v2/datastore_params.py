# -*- coding: utf-8 -*-


class DatastoreParams(object):

    """Implementation of the 'Datastore params.' model.

    Specifies the datastore params.

    Attributes:
        id (long|int): Specifies the Id of the datastore.
        max_concurrent_streams (int): Specifies the max concurrent stream per
            datastore.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "max_concurrent_streams":'maxConcurrentStreams'
    }

    def __init__(self,
                 id=None,
                 max_concurrent_streams=None):
        """Constructor for the DatastoreParams class"""

        # Initialize members of the class
        self.id = id
        self.max_concurrent_streams = max_concurrent_streams


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
        id = dictionary.get('id')
        max_concurrent_streams = dictionary.get('maxConcurrentStreams')

        # Return an object of this model
        return cls(id,
                   max_concurrent_streams)


