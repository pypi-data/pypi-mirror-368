# -*- coding: utf-8 -*-


class RecoverTarget(object):

    """Implementation of the 'Recover Target.' model.

    Specifies the target entity to recover to.

    Attributes:
        id (long|int): Specifies the id of the object.
        name (string): Specifies the name of the object.
        parent_source_id (long|int): Specifies the id of the parent source of
            the target.
        parent_source_name (string): Specifies the name of the parent source
            of the target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "parent_source_id":'parentSourceId',
        "parent_source_name":'parentSourceName'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 parent_source_id=None,
                 parent_source_name=None):
        """Constructor for the RecoverTarget class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.parent_source_id = parent_source_id
        self.parent_source_name = parent_source_name


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
        name = dictionary.get('name')
        parent_source_id = dictionary.get('parentSourceId')
        parent_source_name = dictionary.get('parentSourceName')

        # Return an object of this model
        return cls(id,
                   name,
                   parent_source_id,
                   parent_source_name)


