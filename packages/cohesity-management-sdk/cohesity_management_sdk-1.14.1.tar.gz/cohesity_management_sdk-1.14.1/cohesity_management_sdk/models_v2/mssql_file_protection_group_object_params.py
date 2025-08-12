# -*- coding: utf-8 -*-


class MSSQLFileProtectionGroupObjectParams(object):

    """Implementation of the 'MSSQL File Protection Group Object params.' model.

    Specifies the object params to create File based MSSQL Protection Group.

    Attributes:
        id (long|int): Specifies the ID of the object being protected. If this
            is a non leaf level object, then the object will be auto-protected
            unless leaf objects are specified for exclusion.
        name (string): Specifies the name of the object being protected.
        source_type (string): Specifies the type of source being protected.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "source_type":'sourceType'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 source_type=None):
        """Constructor for the MSSQLFileProtectionGroupObjectParams class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.source_type = source_type


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
        source_type = dictionary.get('sourceType')

        # Return an object of this model
        return cls(id,
                   name,
                   source_type)


