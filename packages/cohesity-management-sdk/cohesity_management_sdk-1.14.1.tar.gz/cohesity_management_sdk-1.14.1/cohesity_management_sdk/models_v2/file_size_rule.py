# -*- coding: utf-8 -*-


class FileSizeRule(object):

    """Implementation of the 'FileSizeRule' model.

    Specifies the file's selection rule by file size. eg.
    1. select files greather than 10 Bytes.
    2. select files less than 20 TiB.
    3. select files greather than 5 MiB.
    type: "object"

    Attributes:
        condition (ConditionEnum): Specifies condition for the file
            selection.
        n_bytes (long|int): Specifies the number of bytes.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "condition":'condition',
        "n_bytes":'nBytes'
    }

    def __init__(self,
                 condition=None,
                 n_bytes=None):
        """Constructor for the FileSizeRule class"""

        # Initialize members of the class
        self.condition = condition
        self.n_bytes = n_bytes


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
        condition = dictionary.get('condition')
        n_bytes = dictionary.get('nBytes')

        # Return an object of this model
        return cls(condition,
                   n_bytes)


