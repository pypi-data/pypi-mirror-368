# -*- coding: utf-8 -*-


class EnumerationOfAllTheSupportedOSTypesForTheUniversalDataAdapter(object):

    """Implementation of the 'Enumeration of all the supported OS types for the Universal Data Adapter.' model.

    Enumeration of all the supported OS types for the Universal Data Adapter.

    Attributes:
        mtype (Type65Enum): Enumeration of all the supported OS types for the
            Universal Data Adapter.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type'
    }

    def __init__(self,
                 mtype=None):
        """Constructor for the EnumerationOfAllTheSupportedOSTypesForTheUniversalDataAdapter class"""

        # Initialize members of the class
        self.mtype = mtype


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
        mtype = dictionary.get('type')

        # Return an object of this model
        return cls(mtype)


