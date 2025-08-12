# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class VersionInfo(object):

    """Implementation of the 'VersionInfo' model.

    Specifies the Id containing the unique identifer and version

    Attributes:
        id (string): Unique identifier for the string entity.
          This field is used to uniquely distinguish different
          entities within the system.
        version (int): Version number associated with the string id.
          This can be used to track different versions of the entity
          id over time. The string ID assigned to the an entity may
          change (infrequently) across software versions.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "version":'version'
    }

    def __init__(self,
                 id=None,
                 version=None):
        """Constructor for the VersionInfo class"""

        # Initialize members of the class
        self.id = id
        self.version = version


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
        version = dictionary.get('version')

        # Return an object of this model
        return cls(id,
                   version)