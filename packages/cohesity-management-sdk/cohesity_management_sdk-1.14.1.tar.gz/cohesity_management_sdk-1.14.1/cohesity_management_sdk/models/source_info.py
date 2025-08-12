# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class SourceInfo(object):

    """Implementation of the 'SourceInfo' model.

    Contains the id and name of the Source.

    Attributes:
        id (long|int): Id of the source.
        name (string): Display Name of the source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id": 'id',
        "name": 'name'
    }

    def __init__(self,
                 id=None,
                 name=None):
        """Constructor for the SourceInfo class"""

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
        id = dictionary.get('id', None)
        name = dictionary.get('name', None)

        # Return an object of this model
        return cls(id,
                   name)


