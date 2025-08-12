# -*- coding: utf-8 -*-


class ArchivalTargets(object):

    """Implementation of the 'ArchivalTargets' model.

    Archival Targets

    Attributes:
        archival_targets (ArchivalTargets1Enum): Specifies the archival
            target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "archival_targets":'archivalTargets'
    }

    def __init__(self,
                 archival_targets=None):
        """Constructor for the ArchivalTargets class"""

        # Initialize members of the class
        self.archival_targets = archival_targets


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
        archival_targets = dictionary.get('archivalTargets')

        # Return an object of this model
        return cls(archival_targets)


