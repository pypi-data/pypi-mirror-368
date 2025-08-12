# -*- coding: utf-8 -*-


class FixedIssue(object):

    """Implementation of the 'Fixed Issue.' model.

    Specifies the description of a fixed issue.

    Attributes:
        id (long|int): Specifies a unique number of the bug.
        release_note (string): Specifies the description of fix made for the
            issue.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "release_note":'releaseNote'
    }

    def __init__(self,
                 id=None,
                 release_note=None):
        """Constructor for the FixedIssue class"""

        # Initialize members of the class
        self.id = id
        self.release_note = release_note


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
        id = dictionary.get('id')
        release_note = dictionary.get('releaseNote')

        # Return an object of this model
        return cls(id,
                   release_note)


