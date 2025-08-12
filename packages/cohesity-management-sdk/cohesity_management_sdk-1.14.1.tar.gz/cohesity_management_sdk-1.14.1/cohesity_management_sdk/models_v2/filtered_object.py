# -*- coding: utf-8 -*-


class FilteredObject(object):

    """Implementation of the 'FilteredObject' model.

    Specifies the filter details.

    Attributes:
        id (long|int): Specifies object id.
        source_id (long|int): Specifies the source id to which this object
            belongs to.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "source_id":'sourceId'
    }

    def __init__(self,
                 id=None,
                 source_id=None):
        """Constructor for the FilteredObject class"""

        # Initialize members of the class
        self.id = id
        self.source_id = source_id


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
        source_id = dictionary.get('sourceId')

        # Return an object of this model
        return cls(id,
                   source_id)


