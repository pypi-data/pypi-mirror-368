# -*- coding: utf-8 -*-


class ADClassConstants(object):

    """Implementation of the 'AD Class Constants' model.

    AD Class Constants

    Attributes:
        ad_class_constants (AdClassConstants1Enum): AD Class Constants

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "ad_class_constants":'adClassConstants'
    }

    def __init__(self,
                 ad_class_constants=None):
        """Constructor for the ADClassConstants class"""

        # Initialize members of the class
        self.ad_class_constants = ad_class_constants


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
        ad_class_constants = dictionary.get('adClassConstants')

        # Return an object of this model
        return cls(ad_class_constants)


