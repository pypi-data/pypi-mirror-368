# -*- coding: utf-8 -*-


class ActionObjectMapping(object):

    """Implementation of the 'ActionObjectMapping' model.

    Specifies the object paring for performing action on list of objects.

    Attributes:
        source_object_id (long|int): Specifies the source object id.
        destination_object_id (long|int): Specifies the destination object
            id.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_object_id":'sourceObjectId',
        "destination_object_id":'destinationObjectId'
    }

    def __init__(self,
                 source_object_id=None,
                 destination_object_id=None):
        """Constructor for the ActionObjectMapping class"""

        # Initialize members of the class
        self.source_object_id = source_object_id
        self.destination_object_id = destination_object_id


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
        source_object_id = dictionary.get('sourceObjectId')
        destination_object_id = dictionary.get('destinationObjectId')

        # Return an object of this model
        return cls(source_object_id,
                   destination_object_id)


