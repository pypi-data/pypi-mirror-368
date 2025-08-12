# -*- coding: utf-8 -*-


class DataTieringTaskFileSizeRuleConditionType(object):

    """Implementation of the 'Data tiering task file size rule condition type.' model.

    Data tiering task file size rule condition type.

    Attributes:
        mtype (Type26Enum): Specifies the data tiering task file size rule
            condition type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type'
    }

    def __init__(self,
                 mtype=None):
        """Constructor for the DataTieringTaskFileSizeRuleConditionType class"""

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


