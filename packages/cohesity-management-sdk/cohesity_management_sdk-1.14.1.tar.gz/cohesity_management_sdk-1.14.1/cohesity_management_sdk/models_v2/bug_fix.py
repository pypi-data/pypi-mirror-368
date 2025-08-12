# -*- coding: utf-8 -*-


class BugFix(object):

    """Implementation of the 'Bug Fix.' model.

    Specifies the description of a bug fix.

    Attributes:
        id (long|int): Specifies a unique number of the bug.
        detail (string): Specifies the description of fix made for the bug.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "detail":'detail'
    }

    def __init__(self,
                 id=None,
                 detail=None):
        """Constructor for the BugFix class"""

        # Initialize members of the class
        self.id = id
        self.detail = detail


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
        detail = dictionary.get('detail')

        # Return an object of this model
        return cls(id,
                   detail)


