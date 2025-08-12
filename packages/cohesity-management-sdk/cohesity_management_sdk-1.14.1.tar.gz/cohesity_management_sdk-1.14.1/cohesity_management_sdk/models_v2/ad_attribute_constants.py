# -*- coding: utf-8 -*-


class ADAttributeConstants(object):

    """Implementation of the 'AD Attribute Constants' model.

    AD Attribute Constants

    Attributes:
        ad_attribute_constants (AdAttributeConstants1Enum): AD Attribute
            Constants

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "ad_attribute_constants":'adAttributeConstants'
    }

    def __init__(self,
                 ad_attribute_constants=None):
        """Constructor for the ADAttributeConstants class"""

        # Initialize members of the class
        self.ad_attribute_constants = ad_attribute_constants


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
        ad_attribute_constants = dictionary.get('adAttributeConstants')

        # Return an object of this model
        return cls(ad_attribute_constants)


