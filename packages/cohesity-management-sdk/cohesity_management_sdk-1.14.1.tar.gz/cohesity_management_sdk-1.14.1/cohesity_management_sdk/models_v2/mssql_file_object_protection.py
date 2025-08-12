# -*- coding: utf-8 -*-


class MssqlFileObjectProtection(object):

    """Implementation of the 'MssqlFileObjectProtection' model.

    Specifies the object params to create File based MSSQL Object Protection

    Attributes:
        id (long|int): Specifies the ID of the object being protected. If this
            is a non leaf level object, then the object will be auto-protected
            unless leaf objects are specified for exclusion.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id'
    }

    def __init__(self,
                 id=None):
        """Constructor for the MssqlFileObjectProtection class"""

        # Initialize members of the class
        self.id = id


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

        # Return an object of this model
        return cls(id)


