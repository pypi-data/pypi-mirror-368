# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.



class EntityIdentifiers(object):

    """Implementation of the 'EntityIdentifiers' model.

   Specifies the identifiers for an entity

    Attributes:
        documentation_link (string): Specifies the link to documentation or additional information about the
          entity. This URL can be used to access more detailed information,
          guidelines, or metadata related to the entity id. It helps in
          understanding the context or usage of the entity id.
        key (string): Specifies the type of identifier. For example, a Virtual Machine (VM) can
          be identified through various types of IDs, such as UUID, Managed Object
          Reference (moref), or other unique identifiers.
        value (string): Specifies the value of the identifier corresponding to the type specified
          in the key.
        version (int): Specifies the version number associated with this EntityIdentifier
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "documentation_link":'documentationLink',
        "key":'key',
        "value":'value',
        "version":'version'
    }

    def __init__(self,
                 documentation_link=None,
                 key=None,
                 value=None,
                 version=None):
        """Constructor for the EntityIdentifiers class"""

        # Initialize members of the class
        self.documentation_link = documentation_link
        self.key = key
        self.value = value
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
        documentation_link = dictionary.get('documentationLink')
        key = dictionary.get('key')
        value = dictionary.get('value')
        version = dictionary.get('version')

        # Return an object of this model
        return cls(documentation_link,
                   key,
                   value,
                   version)