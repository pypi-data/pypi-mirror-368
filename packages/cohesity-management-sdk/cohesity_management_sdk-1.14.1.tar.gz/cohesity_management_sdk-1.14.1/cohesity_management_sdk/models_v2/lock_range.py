# -*- coding: utf-8 -*-

class LockRange(object):

    """Implementation of the 'LockRange' model.

    Specifies details of an entity lock.

    Attributes:
        offset (int): Specifies the offset of an entity lock.
        length (int): Specifies the length of an entity lock.
        is_exclusive (bool): Specifies if entity lock is exclusive.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "offset":'offset',
        "length":'length',
        "is_exclusive":'isExclusive'
    }

    def __init__(self,
                 offset=None,
                 length=None,
                 is_exclusive=None):
        """Constructor for the LockRange class"""

        # Initialize members of the class
        self.offset = offset
        self.length = length
        self.is_exclusive = is_exclusive


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
        offset = dictionary.get('offset')
        length = dictionary.get('length')
        is_exclusive = dictionary.get('isExclusive')

        # Return an object of this model
        return cls(offset,
                   length,
                   is_exclusive)


