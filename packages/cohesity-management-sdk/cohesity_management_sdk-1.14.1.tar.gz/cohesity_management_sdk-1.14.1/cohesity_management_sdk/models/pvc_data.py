# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class PVCData(object):

    """Implementation of the 'PVCData' model.

    Message encapsulating a persistent volume claim

    Attributes:
        logical_size_in_bytes (long|int): Size of the PVC.
        name (string): Name of the persistent volume claim.
        uuid (string): UUID of the PVC.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "logical_size_in_bytes":'logicalSizeInBytes',
        "name":'name',
        "uuid":'uuid'
    }

    def __init__(self,
                 logical_size_in_bytes=None,
                 name=None,
                 uuid=None):
        """Constructor for the PVCData class"""

        # Initialize members of the class
        self.logical_size_in_bytes = logical_size_in_bytes
        self.name = name
        self.uuid = uuid


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
        logical_size_in_bytes = dictionary.get('logicalSizeInBytes')
        name = dictionary.get('name')
        uuid = dictionary.get('uuid')

        # Return an object of this model
        return cls(logical_size_in_bytes,
                   name,
                   uuid)


