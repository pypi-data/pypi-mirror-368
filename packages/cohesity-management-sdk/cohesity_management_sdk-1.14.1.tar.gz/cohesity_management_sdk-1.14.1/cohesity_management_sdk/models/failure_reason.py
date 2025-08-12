# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class FailureReason(object):

    """Implementation of the 'FailureReason' model.

    Failure reason 

    Attributes:
        code (string): TODO: Type description here.
        summary (string): TODO: Type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "code": 'code',
        "summary": 'summary'
    }

    def __init__(self,
                 code=None,
                 summary=None):
        """Constructor for the FailureReason class"""

        # Initialize members of the class
        self.code = code
        self.summary = summary


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
        code = dictionary.get('code', None)
        summary = dictionary.get('summary', None)

        # Return an object of this model
        return cls(code,
                   summary)


