# -*- coding: utf-8 -*-


class UpTieringFileSelection(object):

    """Implementation of the 'UpTieringFileSelection' model.

    Specifies the file's selection rule for uptiering.

    Attributes:
        mtype (Type8Enum): Specifies the metadata information used for the
            file selection.
        value (long|int): Specifies the number of msecs used during the file
            selection eg. 1. select files last accessed 2 weeks ago. 2. select
            files last modified 1 month ago.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type',
        "value":'value'
    }

    def __init__(self,
                 mtype=None,
                 value=None):
        """Constructor for the UpTieringFileSelection class"""

        # Initialize members of the class
        self.mtype = mtype
        self.value = value


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
        value = dictionary.get('value')

        # Return an object of this model
        return cls(mtype,
                   value)


