# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class Entity_StorageClassInfo(object):

    """Implementation of the 'Entity_StorageClassInfo' model.

    Attributes:
        name (string):  Name of the storage class.
        provisioner (string):  Name of the storage provisioner.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name": 'name',
        "provisioner": 'provisioner'
    }

    def __init__(self,
                 name=None,
                 provisioner=None):
        """Constructor for the Entity_StorageClassInfo class"""

        # Initialize members of the class
        self.name = name
        self.provisioner = provisioner


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
        name = dictionary.get('name', None)
        provisioner = dictionary.get('provisioner', None)

        # Return an object of this model
        return cls(name,
                   provisioner)


