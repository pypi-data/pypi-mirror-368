# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.



class CommonFilterExpression_FilterPolicy(object):

    """Implementation of the 'CommonFilterExpression_FilterPolicy' model.

    Message that encapsulates information about any filter policy. Environment
      specific policies are defined as extensions to this proto.

    Attributes:
    """

    # Create a mapping from Model property names to API property names
    _names = {
    }

    def __init__(self):
        """Constructor for the CommonFilterExpression_FilterPolicy class"""

        # Initialize members of the class


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

        # Return an object of this model
        return cls()