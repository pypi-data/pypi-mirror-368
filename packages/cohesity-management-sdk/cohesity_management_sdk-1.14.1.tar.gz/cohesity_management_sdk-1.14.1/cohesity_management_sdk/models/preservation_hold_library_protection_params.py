# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class PreservationHoldLibraryProtectionParams(object):

    """Implementation of the 'PreservationHoldLibraryProtectionParams' model.

    Specifies params specific to protecting the preservation hold library.

    Attributes:
        should_protect_phl (bool): Whether or not the preservation hold library
            should be protected.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "should_protect_phl":'shouldProtectPhl'
    }

    def __init__(self,
                 should_protect_phl=None):
        """Constructor for the PreservationHoldLibraryProtectionParams class"""

        # Initialize members of the class
        self.should_protect_phl = should_protect_phl


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
        should_protect_phl = dictionary.get('shouldProtectPhl')

        # Return an object of this model
        return cls(should_protect_phl)


