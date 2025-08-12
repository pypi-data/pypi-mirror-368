# -*- coding: utf-8 -*-


class UdaObjectParams(object):

    """Implementation of the 'UdaObjectParams' model.

    Specifies the common parameters for UDA objects.

    Attributes:
        has_entity_support (bool): Specifies whether this Object belongs to a
           source having entity support.
        source_type (string): Specifies the source type for Universal Data Adapter object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "has_entity_support":'hasEntitySupport',
        "source_type":'sourceType'
    }

    def __init__(self,
                 has_entity_support=None,
                 source_type=None):
        """Constructor for the UdaObjectParams class"""

        # Initialize members of the class
        self.has_entity_support = has_entity_support
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
        has_entity_support = dictionary.get('hasEntitySupport')
        source_type = dictionary.get('sourceType')

        # Return an object of this model
        return cls(has_entity_support,
                   source_type)