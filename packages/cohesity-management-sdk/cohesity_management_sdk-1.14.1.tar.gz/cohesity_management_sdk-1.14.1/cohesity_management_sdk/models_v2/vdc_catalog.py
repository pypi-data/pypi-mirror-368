# -*- coding: utf-8 -*-


class VDCCatalog(object):

    """Implementation of the 'VDC Catalog' model.

    Specifies a VDC Catalog.

    Attributes:
        uuid (string): Specifies the UUID of the catalog.
        name (string): Specifies the name of the catalog.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "uuid":'uuid',
        "name":'name'
    }

    def __init__(self,
                 uuid=None,
                 name=None):
        """Constructor for the VDCCatalog class"""

        # Initialize members of the class
        self.uuid = uuid
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
        uuid = dictionary.get('uuid')
        name = dictionary.get('name')

        # Return an object of this model
        return cls(uuid,
                   name)


