# -*- coding: utf-8 -*-


class NodeRemovalParameters(object):

    """Implementation of the 'Node Removal Parameters.' model.

    Specifies parameters to initiate/cancel node removal.

    Attributes:
        cancel (bool): If true, cancels node removal that is already in
            progress.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cancel":'cancel'
    }

    def __init__(self,
                 cancel=None):
        """Constructor for the NodeRemovalParameters class"""

        # Initialize members of the class
        self.cancel = cancel


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
        cancel = dictionary.get('cancel')

        # Return an object of this model
        return cls(cancel)


