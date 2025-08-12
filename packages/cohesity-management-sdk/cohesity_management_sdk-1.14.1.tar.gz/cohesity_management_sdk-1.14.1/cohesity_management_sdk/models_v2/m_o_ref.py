# -*- coding: utf-8 -*-


class MORef(object):

    """Implementation of the 'MORef' model.

    Specifies the MoRef for a VMware object.

    Attributes:
        item (string): Unique identifier for the object type.
        type (string): Specifies the type of VMware object

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "item":'item',
        "mtype":'type'
    }

    def __init__(self,
                 item=None,
                 mtype=None):
        """Constructor for the MORef class"""

        # Initialize members of the class
        self.item = item
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
        item = dictionary.get('item')
        mtype = dictionary.get('type')

        # Return an object of this model
        return cls(item,
                   mtype)