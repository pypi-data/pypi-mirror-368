# -*- coding: utf-8 -*-


class Office365PreservationLibraryHoldParams(object):

    """Implementation of the 'Office365PreservationLibraryHoldParams' model.

    Specifies the parameters specific to the protection of the Preservation
      Hold library. The Preservation Hold library is a hidden system location that
      isn't designed to be used interactively but instead, automatically stores files
      when this is needed for compliance reasons. It's not supported to edit, delete,
      or move these automatically retained files yourself. Instead, use compliance
      tools, such as those supported by eDiscovery to access these files.

    Attributes:
        should_protect (bool): Specifies whether to protect the preservation hold library drive
          if one exists. Default is false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "should_protect":'shouldProtect'
    }

    def __init__(self,
                 should_protect=None):
        """Constructor for the Office365PreservationLibraryHoldParams class"""

        # Initialize members of the class
        self.should_protect = should_protect



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
        should_protect = dictionary.get('shouldProtect')

        # Return an object of this model
        return cls(should_protect)