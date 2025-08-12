# -*- coding: utf-8 -*-


class DbOptionGroup(object):

    """Implementation of the 'DbOptionGroup' model.

    Specifies entity representing the RDS option group to use while restoring
    the DB.

    Attributes:
        id (long|int): Specifies the id of the object.
        name (string): Specifies the name of the object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name'
    }

    def __init__(self,
                 id=None,
                 name=None):
        """Constructor for the DbOptionGroup class"""

        # Initialize members of the class
        self.id = id
        self.name = name


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

        # Return an object of this model
        return cls(id,
                   name)


